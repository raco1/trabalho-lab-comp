import streamlit as st

from database.db import conectarBanco

conectarBanco() # Verifica se o banco está conectado/funcionando.

login = st.Page(
    page="pages/login.py",
    title="Log in",
    default=True
)

dashboard = st.Page(
    page="pages/dashboard.py",
    title="Dashboard",
)

sign_up = st.Page(
    page="pages/signup.py",
    title="Sign Up",
)

agendamentos = st.Page(
    page="pages/agendamentos.py",
    title="Agendamentos",
)

recover_psswd = st.Page(
    page="pages/recover_psswd.py",
    title="Recover password",
)

pg = st.navigation([login, dashboard, sign_up, agendamentos, recover_psswd], position="hidden")

pg.run()