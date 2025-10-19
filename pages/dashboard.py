import streamlit as st
import pandas as pd
from database.db import getConexao

st.title("Dashboard")
conn = getConexao()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * from agendamentos WHERE user_id = 1")
agendamentos = cursor.fetchall()

salas = []
horario_comeca = []
horario_termina = []
data_agendada = []
status = []

for agendamento in agendamentos:
    cursor.execute("SELECT * FROM salas WHERE id = %s", (agendamento['key_id'],))
    chave = cursor.fetchone()

    cursor.execute("SELECT start_at, end_at FROM horarios WHERE id = %s", (agendamento['horario_id'],))
    horario = cursor.fetchone()

    salas.append(chave['number'])
    horario_comeca.append(horario['start_at'])
    horario_termina.append(horario['end_at'])
    data_agendada.append(agendamento['data_agendamento'])
    status.append("🟢 Ativo" if agendamento['status'] == 'disponivel' else "🔴 Cancelado" if agendamento['status'] == 'cancelado' else "🟡 Pendente")

cursor.execute("SELECT nome FROM usuarios WHERE id = %s", (agendamento['user_id'],))
usuario = cursor.fetchone()

st.header(f"🔥 Bem-vindo(a) {usuario['nome']}")
st.subheader(f"🗓️ Aqui estão seus agendamentos:")

agendamentos_marcados = pd.DataFrame({
    "sala": salas,
    "data": data_agendada,
    "inicio": horario_comeca,
    "fim": horario_termina,
    "status": status
    })

st.dataframe(
    agendamentos_marcados,
    column_config={
        "sala": "🏫 Sala",
        "data": "📅 Dia da reserva",
        "inicio": "🕐 Início",
        "fim": "🕒 Fim",
        "status": "🔔 Status",
    },
    hide_index=True
)