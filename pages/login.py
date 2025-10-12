import streamlit as st
from services.db import getApi

st.title("Log in ➡️")
st.caption("Por favor, entre com seu email e senha para continuar.")

with st.form("login_form"):
    try:
        user = st.text_input("Usuário", key="user", placeholder="Usuário")
        psswd = st.text_input("Senha", key="psswd", type="password", placeholder="Senha")
        if st.form_submit_button("Login", type='primary', use_container_width=True):
            if not user or not psswd:
                st.warning("⚠️ Preencha todos os campos!")
            else:
                ra = int(user)
                conexao = getApi()
                if conexao:
                    cursor = conexao.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM users WHERE RA = %s", (ra,))
                    usuario = cursor.fetchone()
                    if not usuario:
                        st.warning("❌ Usuário e/ou senha incorretos.")
                    elif ra != usuario['RA']:
                        st.warning("❌ Usuário e/ou senha incorretos.")
                    elif psswd != usuario['senha']:
                        st.warning("❌ Usuário e/ou senha incorretos.")
                    else:
                        st.success(f"🚀 Bem-vindo {usuario['nome']}")
    except Exception as e:
        st.error(f"🔴 Erro ao tentar entrar: {e}")
    col1, col2, col3 = st.columns(3, vertical_alignment="center")
    with col1:
        st.checkbox("Lembrar de mim?", key="remember")   
    with col2:   
        st.page_link("pages/recover_psswd.py", label="Esqueceu a senha?", use_container_width=True)  
    with col3:
        st.page_link("pages/signup.py", label="Criar conta", use_container_width=True)