import time
import streamlit as st
from database.db import iniciarConexao

if 'usuario' not in st.session_state or st.session_state.usuario == None: #tratativa para não ser possível criar uma conta já estando logado no app
    st.title('Criar conta 🆕')
    with st.form('create_acc_form'):
        nome = st.text_input("Nome", key='name', placeholder="Pedro Alves")
        email = st.text_input("Email", key='email', placeholder="exemplo@uniube.br")
        senha = st.text_input("Senha", key='senha', type='password')
        ra = st.text_input("Informe seu RA", key='ra', placeholder="123456")
        if st.form_submit_button("Criar conta", type='primary', use_container_width=True):
            if not nome or not email or not senha or not ra:
                st.warning("⚠️ Preencha todos os campos!")
            else:
                try:                
                    conn = iniciarConexao()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,)) #aqui faz uma tratativa, para nao haver cadastros com mesmo e-mail
                    if cursor.fetchone():
                        st.warning("⚠️ Usuário já cadastrado.")
                    else:
                        cursor.execute("SELECT * FROM usuarios WHERE ra = %s", (ra,)) #aqui também há uma tratativa para evitar usuarios com RA's repetidos
                        if cursor.fetchone():
                            st.warning("⚠️ Usuário já cadastrado.")
                        else:
                            cursor.execute(
                                "INSERT INTO usuarios (ra, nome, email, senha) VALUES (%s, %s, %s, %s)", #se estiver tudo correto, faz um insert na tabela usuarios com os dados informados
                                (ra, nome, email, senha)
                            )
                            conn.commit()
                            cursor.close()
                            conn.close()
                            placeholder = st.empty()
                            placeholder.progress(0, "Cadastrando novo usuário...")
                            time.sleep(2)
                            placeholder.progress(100, "Tudo pronto!")
                            time.sleep(1)
                            st.success("✅ Conta criada com sucesso!")
                            time.sleep(2)
                            st.switch_page("pages/login.py")
                except Exception as e:
                    st.error(f"Erro ao criar conta: {e}")

        
    if st.button("Já possui conta? Faça o Login ✨", use_container_width=True):
        st.switch_page("pages/login.py")