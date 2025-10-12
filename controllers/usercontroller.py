import streamlit as st
from services.db import getApi

def create(nome, email, senha, ra):
        try:                
            conexao = getApi()
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                st.warning("⚠️ Usuário já cadastrado.")
                return
            else:
                cursor.execute("SELECT * FROM users WHERE RA = %s", (ra,))
                if cursor.fetchone():
                    st.warning("⚠️ Usuário já cadastrado.")
                    return
                else:
                    cursor.execute(
                        "INSERT INTO users (RA, nome, email, senha) VALUES (%s, %s, %s, %s)", 
                        (ra, nome, email, senha)
                    )
                    conexao.commit()
                    st.success("✅ Conta criada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao criar conta: {e}")