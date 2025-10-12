import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Carregando as variáveis de ambiente do arquivo .env
load_dotenv()

def conectarBanco():
    """Chamar essa func no em app.py garante que o banco exista antes de abrir o app"""
    try:
        conexao = mysql.connector.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DATABASE"),
            auth_plugin=os.getenv("AUTH_PLUGIN")
        )
        cursor = conexao.cursor()
        db_name = os.getenv("DATABASE")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
        cursor.close()
        conexao.close()
        print("✅ Banco de dados verificado ou criado com sucesso.")
    except Error as e:
        print(f"Erro ao conectar ou criar banco: {e}")

def api():
    """Conecta diretamente ao banco existente."""
    try:
        conexao = mysql.connector.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DATABASE"),
            auth_plugin=os.getenv("AUTH_PLUGIN")
        )
        return conexao
    except Error as e:
        print(f"Erro ao conectar ao banco ScanKey: {e}")
        return None