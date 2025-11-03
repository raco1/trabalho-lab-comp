import cv2
import time
import numpy as np
import streamlit as st
from database.db import iniciarConexao
from datetime import date, datetime, timedelta
from streamlit_local_storage import LocalStorage

localS = LocalStorage()

usuario = localS.getItem("usuario")

st.title("Solicitar sala com urgência 🚨")
st.warning("Essa funcionalidade permite o usuário agendar com urgência horários que estejam 'em cima da hora'.")
with st.container(border=True):
    today = date.today()
    st.header("Data de hoje:")
    select_date = st.date_input("Escolha uma data", min_value=today, label_visibility="hidden", disabled=True)
    
select_date_formatado = select_date.strftime("%d/%m")

try:
    conn = iniciarConexao()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM salas")
    salas = cursor.fetchall() #Isso retorna algo: salas = [{id: 1, number: 214}, {id: 2, number: 215}, ...]

    with st.container(border=True):
        st.subheader("Escolha uma sala:")
        sala_opcao = st.radio(
            "Selecione a sala:",
            [f"Sala {s['number']}" for s in salas], # s['number] é uma lista de salas com apenas os valores de 'number'. Ex: [214, 215, 216, ...]. Esse for cria um radio para cada item dessa lista 
            horizontal=True,
            key="radio_sala",
            label_visibility="hidden"
        )

    sala_selecionada = None
    for s in salas:
        if f"Sala {s['number']}" == sala_opcao: # Se a sala que você selecionou no for acima for igual ao valor de s['number], então coloque os dados (id e number) dessa sala na variavel sala_selecionada
            sala_selecionada = s # se você selecionou a sala 214, por exemplo, sala_selecionada = {'id': 1, 'number': 214} seria algo assim.
            break

    if sala_selecionada:
        cursor.execute("""
            SELECT key_id, horario_id, start_at, end_at
            FROM disponibilidade_sala_data
            JOIN horarios ON horario_id = horarios.id
            WHERE key_id = %s
            AND data_disponibilidade = %s
            AND status <> 'indisponivel';
        """, (sala_selecionada['id'], select_date)) # Essa lógica busca os ids dos horarios disponiveis relacionados à sala que vc selecionou.
        horarios = cursor.fetchall()

        if horarios:
            agora = datetime.now().time()  # horário atual (ex: 08:35)
            horarios_validos = []

            for h in horarios: # filtrar apenas horários que ainda não começaram
                hora_inicio = datetime.strptime(h["start_at"], "%H:%M").time()
                if hora_inicio > agora:
                    horarios_validos.append(h)

            def ordenar_por_horario(horario): # ordenar a lista de horários válidos pelo horário de início
                return horario["start_at"]

            horarios_validos = sorted(horarios_validos, key=ordenar_por_horario)

            if len(horarios_validos) > 0: # pegar o primeiro horário futuro (o mais próximo)
                proximo_horario = horarios_validos[0]
            else:
                proximo_horario = None

            if proximo_horario: # exibir e permitir o agendamento
                with st.container(border=True):
                    st.subheader(f"📅 Próximo horário disponível ({select_date_formatado}):")
                    st.info(f"{proximo_horario['start_at']} - {proximo_horario['end_at']}")
                    #daqui pra baixo é a mesma lógica em dashboard.py para iniciar uma aula, com a diferença que o commit abaixo, INSERE um novo agendamento ao invés de dar um UPDATE em um agendamento ja existente
                    confirmar = st.button("📅 Scanear QrCode para começar aula!", use_container_width=True)
                    if "mostrar_camera" not in st.session_state:
                        st.session_state["mostrar_camera"] = False

                    if confirmar:
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
                                cursor.execute("INSERT INTO agendamentos (user_id, key_id, data_agendamento, horario_id, status, created_at) VALUES (%s, %s, %s, %s, %s, %s)", (usuario["id"], sala_selecionada['id'], select_date, proximo_horario['horario_id'], 'ativo', datetime.now()))
                                conn.commit()
                                st.session_state["mostrar_camera"] = False  # fecha após ler
                                placeholder = st.empty()
                                placeholder.progress(0, "Iniciando agendamento...")
                                time.sleep(1)
                                placeholder.progress(30, "Confirmando a sala...")
                                time.sleep(1)
                                placeholder.progress(60, "Confirmando o horário...")
                                time.sleep(1)
                                placeholder.progress(100, "Quase pronto...")
                                time.sleep(1)
                                st.success(f"🚀 Agendamento confirmado para {sala_opcao} às {proximo_horario['start_at']}") #mensagem de sucesso na criação do agendamento
                                time.sleep(2) # apos 2s ele redireciona o usuario para o dashboard
                                st.switch_page("pages/dashboard.py")
                        else:
                            st.warning("⚠️ Nenhum QR Code detectado.")    
            else:
                st.warning("⚠️ Nenhum horário futuro disponível para hoje.")

    else:
        st.info("Por favor, selecione uma sala.")
except Exception as e:
    st.error(f"Erro ao criar agendamento: {e}")

if st.button("👈 Voltar ao Dashboard", type="primary"):
    st.switch_page("pages/dashboard.py")