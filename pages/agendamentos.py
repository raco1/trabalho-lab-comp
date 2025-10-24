import streamlit as st
import time
from datetime import date, datetime, timedelta
from database.db import iniciarConexao

if 'usuario' not in st.session_state or st.session_state.usuario == None: #Caso não tenha usuário logado, retornar à pagina de login.
    st.switch_page("pages/login.py")

st.title("Solicitar agendamento de sala 🛠️")

with st.container(border=True):
    today = date.today()
    max_days = today + timedelta(days=15)
    st.subheader("Escolha uma data:")
    select_date = st.date_input("Escolha uma data", min_value=today, max_value=max_days, label_visibility="hidden")
    
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
            with st.container(border=True):
                st.subheader(f"Selecione um dos horários disponíveis no dia {select_date_formatado}:")
                horario_opcao = st.radio(
                    "Selecione o horário:",
                    [f"{h['start_at']} - {h['end_at']}" for h in horarios], # mesma ideia para selecionar a sala, aplicada ao horario
                    key="radio_horario",
                    label_visibility="hidden"
                )

            horario_selecionado = None
            for h in horarios:
                if f"{h['start_at']} - {h['end_at']}" == horario_opcao: # mesma ideia para selecionar a sala, aplicada ao horario
                    horario_selecionado = h
                    break

            if horario_selecionado and st.button("📅 Agendar horário!", width="stretch"): #Caso o usuario tenha selecionado tudo certinho, executa o insert na tabela de agendamentos com os dados que ele selecinou.
                cursor.execute("INSERT INTO agendamentos (user_id, key_id, data_agendamento, horario_id, created_at) VALUES (%s, %s, %s, %s, %s)", (st.session_state.usuario["id"], sala_selecionada['id'], select_date, horario_selecionado['horario_id'], datetime.now()))
                conn.commit() #da commit no banco
                cursor.close() #fecha o cursor
                conn.close() #encerra a conexao com o banco
                placeholder = st.empty()
                time.sleep(0.5)
                placeholder.progress(0, "Iniciando agendamento...")
                time.sleep(1)
                placeholder.progress(30, "Confirmando a sala...")
                time.sleep(1)
                placeholder.progress(60, "Confirmando o horário...")
                time.sleep(1)
                placeholder.progress(100, "Quase pronto...")
                time.sleep(1)
                st.success(f"🚀 Agendamento confirmado para {sala_opcao} às {horario_opcao}") #mensagem de sucesso na criação do agendamento
                time.sleep(2) # apos 2s ele redireciona o usuario para o dashboard
                st.switch_page("pages/dashboard.py")
        else:
            st.warning("Nenhum horário disponível para esta sala na data escolhida.") #tratativa caso não tenham horarios disponiveis na data x.
    else:
        st.info("Por favor, selecione uma sala.")
except Exception as e:
    st.error(f"Erro ao criar agendamento: {e}")

if st.button("👈 Voltar ao Dashboard", type="primary"):
    st.switch_page("pages/dashboard.py")