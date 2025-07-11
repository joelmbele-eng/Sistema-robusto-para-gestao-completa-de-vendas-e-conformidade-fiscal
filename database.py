# database.py
import sqlite3
from sqlite3 import Error

DB_NAME = "sistema_vendas.db"

def conectar():
    """Retorna uma conexão com o banco de dados."""
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except Error as e:
        print(f"Erro ao conectar ao banco: {e}")
    return None

def criar_tabelas():
    """Cria as tabelas necessárias, se não existirem."""
    conn = conectar()
    cursor = conn.cursor()
    # Tabela de produtos com campo IVA (percentual)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        categoria TEXT,
        quantidade INTEGER DEFAULT 0,
        preco_detail REAL,
        preco_grosso REAL,
        data_validade TEXT,
        limite_minimo INTEGER DEFAULT 0,
        iva REAL DEFAULT 0
    )
    """)
    # Tabela de vendas com coluna status ("OK" ou "cancelado")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario TEXT,
        data_venda TEXT,
        total REAL,
        detalhes TEXT,
        status TEXT DEFAULT 'OK'
    )
    """)
    # Tabela de usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        senha TEXT NOT NULL,
        tipo TEXT NOT NULL,
        ativo INTEGER DEFAULT 1
    )
    """)
    # Tabela de empresa
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS empresa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        localizacao TEXT,
        provincia TEXT,
        nif TEXT,
        telefone TEXT,
        observacao TEXT
    )
    """)
    # Tabela de solicitações
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS solicitacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_usuario TEXT,
        produto TEXT,
        descricao TEXT,
        data_solicitacao TEXT
    )
    """)
    # Tabela de sessões
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_usuario TEXT,
        hora_entrada TEXT,
        hora_saida TEXT
    )
    """)
    # Tabela de configuração (para papel, impressora, etc.)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS config (
        chave TEXT PRIMARY KEY,
        valor TEXT
    )
    """)
    conn.commit()
    conn.close()

def get_config(chave):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT valor FROM config WHERE chave=?", (chave,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def set_config(chave, valor):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES (?, ?)", (chave, valor))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    criar_tabelas()
    print("Tabelas criadas com sucesso!")
