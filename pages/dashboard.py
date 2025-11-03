import cv2
import time
import numpy as np
import pandas as pd
import streamlit as st
from database.db import iniciarConexao
from datetime import datetime, timedelta
from streamlit_local_storage import LocalStorage

localS = LocalStorage()

usuario = localS.getItem("usuario")

if not usuario: #Caso não tenha usuário logado, retornar à pagina de login.
    st.switch_page("pages/login.py")

conn = iniciarConexao()
cursor = conn.cursor(dictionary=True)

def remover_cancelados_antigos(cursor, conn):
    """
    Remove agendamentos com status 'cancelado' com mais de 2 dias.
    """
    dois_dias_atras = datetime.now() - timedelta(days=2) # pega o dia de hoje - 2 dias
    
    cursor.execute(
        "DELETE FROM agendamentos WHERE status = 'cancelado' AND data_agendamento <= %s",
        (dois_dias_atras,)
    )
    conn.commit()

remover_cancelados_antigos(cursor, conn) # sempre que a pagina dashboard for carregada, os agendamentos cancelados mais antigos que 2 dias não irão aparecer na tabela para evitar poluição
cursor.execute("SELECT * from agendamentos WHERE user_id = %s", (usuario['id'],)) # busca todos os agendamentos com o id do usuario logado na sessao
agendamentos = cursor.fetchall()

ids, salas, status, data_agendada, horario_comeca, horario_termina = [], [], [], [], [], []

for agendamento in agendamentos:
    ids = [a["id"] for a in agendamentos] #cria uma lista com os ids dos agendamentos

    cursor.execute("SELECT * FROM salas WHERE id = %s", (agendamento['key_id'],)) #dentro dos agendamentos buscados acima, busca as salas a partir do id das salas e passa para uma variavel
    chave = cursor.fetchone() #pega o primeiro e retorna algo do tipo: {'id': 3, 'number': 216}

    cursor.execute("SELECT start_at, end_at FROM horarios WHERE id = %s", (agendamento['horario_id'],))#com a mesma ideia das salas, agr com os horarios
    horario = cursor.fetchone()#pega o primeiro e retorna {'start_at': '11:00', 'end_at': '12:00'}

    salas.append(chave['number'])#aqui ele pega os valores 'number' e os coloca dentro da lista de salas, ficando parecido com: salas = [ 216, 216, 232]
    horario_comeca.append(horario['start_at'])#mesma ideia, e retorna algo como: horario_comeca = ['11:00', '18:00']
    horario_termina.append(horario['end_at'])#mesma ideia, e retorna algo como: horario_termina = ['12:00', '18:50']
    data_agendada.append(agendamento['data_agendamento'].strftime("%d/%m/%y"))# armazena as datas na lista e retorna algo do tipo: data_agendada = [datetime.date(2025, 10, 28), datetime.date(2025, 10, 24)]
    status.append("🟢 Ativo" if agendamento['status'] == 'ativo' else "🔴 Cancelado" if agendamento['status'] == 'cancelado' else "🟡 Pendente")
    #faz uma lo´gica que, caso o status esteja 'ativo' ele retorna "🟢 Ativo", caso esteja 'cancelado' retorna "🔴 Cancelado" e por fim, se estiver com qlq outra entrada, retorna "🟡 Pendente"
    #no caso do usuario com id = 1, ele está retornando essa lista status = ['🟡 Pendente', '🟡 Pendente']


#pra ficar mais visivel, esse é o retorno de st.write(st.session_state.usuario)
#{
#    "id":1
#    "ra":"123456"
#    "nome":"Rafael Coelho"
#    "email":"rafaelcoelho@uniube.br"
#    "senha":"123"
#    "role":"teacher"
#}

st.subheader(f"👋Bem-vindo(a), {usuario['nome']} ao") #aqui é buscado o nome do usuario para aparecer no header
st.title(f"EasyRoom✨") 
st.divider()

if "🟢 Ativo" in status: # caso tenha algum agendamento com status ativo, ele mostra somente os detalhes do agendamento ativado
    st.header(f"🟢 Você está em aula:")
    cursor.execute("SELECT * FROM agendamentos WHERE status = 'ativo'")
    aula_em_curso = cursor.fetchone()

    cursor.execute("SELECT start_at, end_at FROM horarios WHERE id = %s", (aula_em_curso['horario_id'],))
    horario_em_curso = cursor.fetchone()

    cursor.execute("SELECT * FROM salas WHERE id = %s", (aula_em_curso['key_id'],))
    sala_em_curso = cursor.fetchone()

    st.subheader(f"Sua aula começou às {horario_em_curso['start_at']} na Sala {sala_em_curso['number']} e tem previsão para encerrar às {horario_em_curso['end_at']}.")

    @st.dialog("Tem certeza de que quer finalizar a aula?", on_dismiss="rerun") # criar o botão para encerrar o agendamento/aula
    def encerrarAula():
        if st.button(" ✅ Sim"):
            cursor.execute("UPDATE agendamentos SET status = 'pendente' WHERE status = 'ativo'")
            conn.commit()
            st.session_state.encerrarAula = True
            st.rerun()
        if st.button(" ❌ Não"):
            st.rerun()
    
    if 'encerrarAula' not in st.session_state:
        if st.button("Encerrar aula", type="primary"):
            encerrarAula()
else:
    if agendamentos: # caso tenha agendamentos pendentes e não tenha nenhum agendamento ativado, irá mostrar a tabela com os agendamentos pendentes:
        st.subheader(f"🗓️ Aqui estão seus agendamentos:")
        agendamentos_marcados = pd.DataFrame({ #aqui pegamos todas as listas criadas acima e atribuimos as colunas do DF
        "id": ids,
        "sala": salas,
        "data": data_agendada,
        "inicio": horario_comeca,
        "fim": horario_termina,
        "status": status
        })


        st.dataframe(
            agendamentos_marcados, #configuramos as colunas
            column_config={
                "id": None,
                "sala": "🏫 Sala",
                "data": "📅 Dia da reserva",
                "inicio": "🕐 Início",
                "fim": "🕒 Fim",
                "status": "🔔 Status",
            },
            hide_index=True
        )

        opcoes = [f"Sala {row['sala']} - Dia {row['data']} - Horário: {row['inicio']}-{row['fim']}" for _, row in agendamentos_marcados.iterrows()]
        selecionado = st.selectbox("🔍 Selecione um agendamento para ver detalhes:", opcoes)
        agora = datetime.now() # data e hora atuais
        if selecionado:
                indice = opcoes.index(selecionado)
                agendamento = agendamentos_marcados.iloc[indice]
                detalhe = st.expander("📄 Detalhes do agendamento selecionado serão exibidos aqui:", expanded=True)
                with detalhe:
                    st.markdown(f"### 🏫 Sala {agendamento['sala']}")
                    st.markdown(f"**📅 Data e Horário:** Dia {agendamento['data']} das {agendamento['inicio']} às {agendamento['fim']}")
                    st.markdown(f"🙋🏻‍♂️ Responsável: {usuario['nome']}")
                    st.markdown(f"**🔔 Status:** {agendamento['status']}")
                    agendamento_id = int(agendamento['id'])
                    if "🟡 Pendente" in agendamento['status']:
                        @st.dialog("Tem certeza de que quer cancelar esse agendamento?", on_dismiss="rerun") # criar o botão para encerrar o agendamento/aula
                        def cancelarAgendamento():
                            if st.button(" ✅ Sim"):
                                cursor.execute("UPDATE agendamentos SET status = 'cancelado' WHERE id = %s", (agendamento_id,))
                                conn.commit()
                                time.sleep(1)
                                st.rerun()
                            if st.button(" ❌ Não"):
                                st.rerun()
                        if 'cancelarAgendamento' not in st.session_state:
                            if st.button("⚠️ Cancelar agendamento ⚠️", type="primary"):
                                cancelarAgendamento()

                    data_ag = datetime.strptime(agendamento['data'], "%d/%m/%y").date() # converte a data e horário do agendamento para datetime completo
                    hora_inicio = datetime.strptime(agendamento['inicio'], "%H:%M").time()
                    inicio_agendamento = datetime.combine(data_ag, hora_inicio) # cria um datetime completo para o horário de início
                    liberacao = inicio_agendamento - timedelta(minutes=10) # define o horário de liberação: 10 minutos antes

                    if agora.date() == data_ag and liberacao <= agora <= inicio_agendamento + timedelta(minutes=10):  # liberacao <= agora <= inicio_agendamento + timedelta(minutes=10) = 2025-11-03 07:55:00 2025-11-03 08:02:36.218204 2025-11-03 08:15:00, ou seja, se agora estiver entre 07:55 e 08:15 e no dia do agendamento, o usuario irá conseguir scanear o qrcode. 
                        if "mostrar_camera" not in st.session_state:
                                st.session_state["mostrar_camera"] = False

                        if st.button("📷 Scannear chave"):
                                st.session_state["mostrar_camera"] = True

                        if st.session_state["mostrar_camera"]:
                                st.title("Leitor de QR Code")
                                camera = st.camera_input("Tire uma foto do QR Code")
                                if camera:
                                    bytes_data = camera.getvalue()
                                    npimg = np.frombuffer(bytes_data, np.uint8)
                                    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
                                    detector = cv2.QRCodeDetector()
                                    data, bbox, _ = detector.detectAndDecode(img)
                                    if data:
                                        cursor.execute("UPDATE agendamentos SET status = 'ativo' WHERE id = %s", usuario['id'])
                                        conn.commit()
                                        st.session_state["mostrar_camera"] = False  # fecha após ler
                                        st.rerun()
                                else:
                                    st.warning("⚠️ Nenhum QR Code detectado.")
    else:
        st.title("Você não possui agendamentos no momento.")

st.divider()

col1, col2, col3 = st.columns([1, 1, 0.3])

with col1:
    if st.button("Solicitar agendamento de sala"): # botao que encaminha o usuario a pagina de criação de agendamento
        st.switch_page("pages/agendamentos.py")

with col2:
    if st.button("Solicitar sala com urgência"): # botao que encaminha o usuario a pagina de criação de uma sala com urgencia (em cima da hora)
        st.switch_page("pages/solicitacao.py")

with col3:
     if st.button("LogOut", type="primary"): # botao de logout
        localS.deleteItem('usuario')
        time.sleep(1)
        st.rerun()
        st.switch_page("pages/login.py")
    