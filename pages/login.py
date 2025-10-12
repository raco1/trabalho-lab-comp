import streamlit as st
from controllers.usercontroller import login

st.title("Log in ➡️")
st.caption("Por favor, entre com seu email e senha para continuar.")

with st.form("login_form"):
    user = st.text_input("Usuário", key="user", placeholder="Usuário")
    psswd = st.text_input("Senha", key="psswd", type="password", placeholder="Senha")
    if st.form_submit_button("Login", type='primary', use_container_width=True):
        if not user or not psswd:
            st.warning("⚠️ Preencha todos os campos!")
        else:
            login(user, psswd)
    col1, col2, col3 = st.columns(3, vertical_alignment="center")
    with col1:
        st.checkbox("Lembrar de mim?", key="remember")   
    with col2:   
        st.page_link("pages/recover_psswd.py", label="Esqueceu a senha?", use_container_width=True)  
    with col3:
        st.page_link("pages/signup.py", label="Criar conta", use_container_width=True)