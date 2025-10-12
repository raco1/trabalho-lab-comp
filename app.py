import streamlit as st

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

appointments = st.Page(
    page="pages/appoitments.py",
    title="Appointments",
)

recover_psswd = st.Page(
    page="pages/recover_psswd.py",
    title="Recover password",
)

pg = st.navigation([login, dashboard, sign_up, appointments, recover_psswd], position="hidden")

pg.run()