import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Carregando as variáveis de ambiente do arquivo .env
load_dotenv()

def conectarBanco():
    """Chamar essa func no em app.py garante que o banco exista antes de abrir o app"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DATABASE"),
            auth_plugin=os.getenv("AUTH_PLUGIN")
        )
        cursor = conn.cursor()
        db_name = os.getenv("DATABASE")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};") #faz esse pequeno teste para verificar se o banco existe
        cursor.close()
        conn.close()
        print("✅ Banco de dados verificado ou criado com sucesso.")
    except Error as e:
        print(f"Erro ao conectar ou criar banco: {e}")

def iniciarConexao():
    """Conecta diretamente ao banco existente."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DATABASE"),
            auth_plugin=os.getenv("AUTH_PLUGIN")
        )
        return conn
    except Error as e:
        print(f"Erro ao conectar ao banco ScanKey: {e}")
        return None
    
def getUsuario(ra):
    """Função se conecta com o banco e retorna todos os usuarios cadastrados."""
    try:
        conn = iniciarConexao()
        cursor  = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE ra = %s", (ra,))
        usuario = cursor.fetchone()
        return usuario
    except Exception as e:
        print(f"Erro ao buscar usuarios: {e}")
        return None