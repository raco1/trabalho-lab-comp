import streamlit as st
import pandas as pd
from database.db import iniciarConexao

if 'usuario' not in st.session_state or st.session_state.usuario == None: #Caso não tenha usuário logado, retornar à pagina de login.
    st.switch_page("pages/login.py")

conn = iniciarConexao()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * from agendamentos WHERE user_id = %s", (st.session_state.usuario['id'],)) # busca todos os agendamentos com o id do usuario logado na sessao
agendamentos = cursor.fetchall()

salas = []
horario_comeca = []
horario_termina = []
data_agendada = []
status = []

for agendamento in agendamentos:
    cursor.execute("SELECT * FROM salas WHERE id = %s", (agendamento['key_id'],)) #dentro dos agendamentos buscados acima, busca as salas a partir do id das salas e passa para uma variavel
    chave = cursor.fetchone() #pega o primeiro e retorna algo do tipo: {'id': 3, 'number': 216}

    cursor.execute("SELECT start_at, end_at FROM horarios WHERE id = %s", (agendamento['horario_id'],))#com a mesma ideia das salas, agr com os horarios
    horario = cursor.fetchone()#pega o primeiro e retorna {'start_at': '11:00', 'end_at': '12:00'}

    salas.append(chave['number'])#aqui ele pega os valores 'number' e os coloca dentro da lista de salas, ficando parecido com: salas = [ 216, 216, 232]
    horario_comeca.append(horario['start_at'])#mesma ideia, e retorna algo como: horario_comeca = ['11:00', '18:00']
    horario_termina.append(horario['end_at'])#mesma ideia, e retorna algo como: horario_termina = ['12:00', '18:50']
    data_agendada.append(agendamento['data_agendamento'])# armazena as datas na lista e retorna algo do tipo: data_agendada = [datetime.date(2025, 10, 28), datetime.date(2025, 10, 24)]
    status.append("🟢 Ativo" if agendamento['status'] == 'disponivel' else "🔴 Cancelado" if agendamento['status'] == 'cancelado' else "🟡 Pendente")
    #faz uma lo´gica que, caso o status esteja 'disponivel' ele retorna "🟢 Ativo", caso esteja 'cancelado' retorna "🔴 Cancelado" e por fim, se estiver com qlq outra entrada, retorna "🟡 Pendente"
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

st.title("Dashboard")
st.header(f"🔥 Bem-vindo(a) {st.session_state.usuario['nome']}") #aqui é buscado o nome do usuario para aparecer no header
st.subheader(f"🗓️ Aqui estão seus agendamentos:")

agendamentos_marcados = pd.DataFrame({ #aqui pegamos todas as listas criadas acima e atribuimos as colunas do DF
    "sala": salas,
    "data": data_agendada,
    "inicio": horario_comeca,
    "fim": horario_termina,
    "status": status
    })

st.dataframe(
    agendamentos_marcados, #configuramos as colunas
    column_config={
        "sala": "🏫 Sala",
        "data": "📅 Dia da reserva",
        "inicio": "🕐 Início",
        "fim": "🕒 Fim",
        "status": "🔔 Status",
    },
    hide_index=True
)

if st.button("Solicitar agendamento"): #botao que encaminha o usuario a pagina de criação de agendamento
    st.switch_page("pages/agendamentos.py")

if st.button("LogOut", type="primary"): #botao de logout
    st.session_state.usuario = None
    st.switch_page("pages/login.py")