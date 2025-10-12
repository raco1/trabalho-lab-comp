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

def login(user, psswd):
    try:
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