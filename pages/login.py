import streamlit as st
from database.db import getUsuario

st.title("Log in ➡️")
st.caption("Por favor, entre com seu email e senha para continuar.")
with st.form("login_form"):
    ra = st.text_input("Usuário", key="ra", placeholder="Usuário")
    senha = st.text_input("Senha", key="senha", type="password", placeholder="Senha")
    if st.form_submit_button("Login", type='primary', use_container_width=True):
        if not ra or not senha:
            st.warning("⚠️ Preencha todos os campos!")
        else:
            usuario = getUsuario(ra)
            if not usuario:
                st.warning("❌ Usuário ou senha incorretos.")
            elif senha != usuario['senha']:
                st.warning("❌ Usuário ou senha incorretos.")
            else:
                st.session_state.usuario = usuario
                st.switch_page("pages/dashboard.py")
with st.container(border=True):
    col1, col2, col3 = st.columns(3, vertical_alignment="center")
    with col1:
            st.checkbox("Lembrar de mim?", key="remember")   
    with col2:   
        if st.button("Esqueceu a senha?🚨", use_container_width=True):
            st.switch_page("pages/recover_psswd.py")
    with col3:
        if st.button("Cadastre-se 🆕", use_container_width=True):
            st.switch_page("pages/signup.py")