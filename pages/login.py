import streamlit as st

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
                st.success(f"🚀 Bem-vindo {user}")
    except Exception as e:
        st.error(f"🔴 Erro ao tentar entrar: {e}")