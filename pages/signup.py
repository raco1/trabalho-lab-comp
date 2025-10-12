import streamlit as st
from controllers.usercontroller import create

st.title('Criar conta 🆕')

with st.form('create_acc_form'):
    nome = st.text_input("Nome", key='name', placeholder="Pedro Alves")
    email = st.text_input("Email", key='email', placeholder="exemplo@uniube.br")
    psswd = st.text_input("Senha", key='senha', type='password')
    ra = st.text_input("Informe seu RA", key='ra', placeholder="123456")
    if st.form_submit_button("Criar conta", type='primary', use_container_width=True):
        if not nome or not email or not psswd or not ra:
            st.warning("⚠️ Preencha todos os campos!")
        else:
            create(nome, email, psswd, ra)
            # st.switch_page("pages/login.py") -> Vai pra pagina de login automaticamente
        