import os
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'clinica_estoque.db')

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                unidade_medida TEXT NOT NULL DEFAULT "unidade",
                fornecedor TEXT,
                preco_unitario DECIMAL(10,2) NOT NULL DEFAULT 0,
                saldo_atual INTEGER NOT NULL DEFAULT 0,
                estoque_minimo INTEGER NOT NULL DEFAULT 10,
                controla_lote BOOLEAN NOT NULL DEFAULT FALSE,
                ativo BOOLEAN NOT NULL DEFAULT TRUE,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                responsavel TEXT NOT NULL,
                destino TEXT NOT NULL,
                custo_unitario DECIMAL(10,2) NOT NULL DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                lido BOOLEAN NOT NULL DEFAULT FALSE,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        ''')
        print("Banco de dados inicializado!")

def listar_produtos():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produtos WHERE ativo = TRUE ORDER BY nome')
        return cursor.fetchall()

def normalizar_codigo(codigo):
    if codigo is None:
        return ''
    return str(codigo).strip().upper()


def validar_produto(codigo, nome, preco_unitario, estoque_minimo):
    codigo = normalizar_codigo(codigo)
    nome = (nome or '').strip()

    if not codigo:
        raise ValueError('Codigo do produto e obrigatorio.')
    if not nome:
        raise ValueError('Nome do produto e obrigatorio.')
    if preco_unitario < 0:
        raise ValueError('Preco unitario nao pode ser negativo.')
    if estoque_minimo < 0:
        raise ValueError('Estoque minimo nao pode ser negativo.')

    return codigo, nome


def cadastrar_produto(codigo, nome, categoria, unidade_medida, fornecedor, preco_unitario, estoque_minimo, controla_lote):
    codigo, nome = validar_produto(codigo, nome, preco_unitario, estoque_minimo)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM produtos WHERE codigo = ? AND ativo = TRUE', (codigo,))
        if cursor.fetchone():
            raise ValueError(f'Ja existe um produto com o codigo {codigo}.')
        cursor.execute('INSERT INTO produtos (codigo, nome, categoria, unidade_medida, fornecedor, preco_unitario, estoque_minimo, controla_lote) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (codigo, nome, categoria, unidade_medida, fornecedor, preco_unitario, estoque_minimo, controla_lote))
        return cursor.lastrowid


def registrar_entrada(produto_id, quantidade, responsavel, destino, custo_unitario):
    if quantidade <= 0:
        raise ValueError('Quantidade deve ser maior que zero.')
    if not responsavel or not responsavel.strip():
        raise ValueError('Responsavel e obrigatorio.')
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, saldo_atual FROM produtos WHERE id = ? AND ativo = TRUE', (produto_id,))
        produto = cursor.fetchone()
        if not produto:
            raise ValueError('Produto nao encontrado.')
        cursor.execute('UPDATE produtos SET saldo_atual = saldo_atual + ? WHERE id = ?', (quantidade, produto_id))
        cursor.execute('INSERT INTO movimentacoes (tipo, produto_id, quantidade, responsavel, destino, custo_unitario) VALUES (?, ?, ?, ?, ?, ?)', ('ENTRADA', produto_id, quantidade, responsavel.strip(), destino, custo_unitario))
        return cursor.lastrowid


def registrar_saida(produto_id, quantidade, responsavel, destino, custo_unitario):
    if quantidade <= 0:
        raise ValueError('Quantidade deve ser maior que zero.')
    if not responsavel or not responsavel.strip():
        raise ValueError('Responsavel e obrigatorio.')
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT saldo_atual FROM produtos WHERE id = ? AND ativo = TRUE', (produto_id,))
        produto = cursor.fetchone()
        if not produto:
            raise ValueError('Produto nao encontrado.')
        if produto['saldo_atual'] < quantidade:
            raise ValueError('Saldo insuficiente para a saida solicitada.')
        cursor.execute('UPDATE produtos SET saldo_atual = saldo_atual - ? WHERE id = ?', (quantidade, produto_id))
        cursor.execute('INSERT INTO movimentacoes (tipo, produto_id, quantidade, responsavel, destino, custo_unitario) VALUES (?, ?, ?, ?, ?, ?)', ('SAIDA', produto_id, quantidade, responsavel.strip(), destino, custo_unitario))
        return cursor.lastrowid

def verificar_alertas():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, codigo, saldo_atual, estoque_minimo FROM produtos WHERE ativo = TRUE AND saldo_atual <= estoque_minimo')
        produtos = cursor.fetchall()
        for produto in produtos:
            cursor.execute('SELECT id FROM alertas WHERE produto_id = ? AND tipo = "ESTOQUE_BAIXO" AND lido = FALSE', (produto['id'],))
            if not cursor.fetchone():
                mensagem = f"Estoque baixo: {produto['nome']} - Saldo: {produto['saldo_atual']}, Minimo: {produto['estoque_minimo']}"
                cursor.execute('INSERT INTO alertas (produto_id, tipo, mensagem) VALUES (?, ?, ?)', (produto['id'], 'ESTOQUE_BAIXO', mensagem))

st.set_page_config(page_title="Controle de Estoque - Clinica", layout="wide")
init_database()

st.sidebar.title("Controle de Estoque")
menu = st.sidebar.radio("Navegacao", ["Dashboard", "Produtos", "Entradas", "Saidas", "Alertas"])

if menu == "Dashboard":
    st.title("Dashboard")
    produtos = listar_produtos()
    total = len(produtos)
    valor = sum(p['saldo_atual'] * p['preco_unitario'] for p in produtos)
    baixo = sum(1 for p in produtos if p['saldo_atual'] <= p['estoque_minimo'])
    c1, c2, c3 = st.columns(3)
    c1.metric("Produtos", total)
    c2.metric("Valor em Estoque", f"R$ {valor:,.2f}")
    c3.metric("Estoque Baixo", baixo)

elif menu == "Produtos":
    st.title("Produtos")
    with st.form("cadastro"):
        codigo = st.text_input("Codigo")
        nome = st.text_input("Nome")
        categoria = st.selectbox("Categoria", ["Medicamentos", "Descartaveis", "Equipamentos", "Exames", "Outros"])
        unidade = st.selectbox("Unidade", ["unidade", "caixa", "pacote", "frasco"])
        fornecedor = st.text_input("Fornecedor")
        preco = st.number_input("Preco", min_value=0.0)
        minimo = st.number_input("Estoque minimo", min_value=0, value=10)
        lote = st.checkbox("Controla lote")
        if st.form_submit_button("Salvar"):
            try:
                cadastrar_produto(codigo.upper(), nome, categoria, unidade, fornecedor, preco, minimo, lote)
                st.success("Produto cadastrado!")
            except Exception as e:
                st.error(f"Erro: {e}")
    produtos = listar_produtos()
    if produtos:
        df = pd.DataFrame(produtos)
        st.dataframe(df, use_container_width=True)

elif menu == "Entradas":
    st.title("Entradas")
    produtos = listar_produtos()
    if produtos:
        opcoes = {f"{p['codigo']} - {p['nome']}": p['id'] for p in produtos}
        with st.form("entrada"):
            produto_sel = st.selectbox("Produto", list(opcoes.keys()))
            qtd = st.number_input("Quantidade", min_value=1)
            resp = st.text_input("Responsavel")
            destino = st.selectbox("Destino", ["Almoxarifado", "Radiologia", "Oftalmologia", "Odontologia", "Nutricao", "Geral"])
            custo = st.number_input("Custo unitario", min_value=0.0)
            if st.form_submit_button("Registrar"):
                try:
                    registrar_entrada(opcoes[produto_sel], qtd, resp, destino, custo)
                    st.success("Entrada registrada!")
                except Exception as e:
                    st.error(f"Erro: {e}")

elif menu == "Saidas":
    st.title("Saidas")
    produtos = listar_produtos()
    if produtos:
        opcoes = {f"{p['codigo']} - {p['nome']}": p['id'] for p in produtos}
        with st.form("saida"):
            produto_sel = st.selectbox("Produto", list(opcoes.keys()))
            qtd = st.number_input("Quantidade", min_value=1)
            resp = st.text_input("Responsavel")
            destino = st.selectbox("Destino", ["Almoxarifado", "Radiologia", "Oftalmologia", "Odontologia", "Nutricao", "Geral"])
            custo = st.number_input("Custo unitario", min_value=0.0)
            if st.form_submit_button("Registrar"):
                try:
                    registrar_saida(opcoes[produto_sel], qtd, resp, destino, custo)
                    st.success("Saida registrada!")
                except Exception as e:
                    st.error(f"Erro: {e}")

elif menu == "Alertas":
    st.title("Alertas")
    verificar_alertas()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT a.*, p.nome as produto_nome FROM alertas a JOIN produtos p ON a.produto_id = p.id WHERE a.lido = FALSE ORDER BY a.criado_em DESC')
        alertas = cursor.fetchall()
    if alertas:
        for alerta in alertas:
            st.error(alerta['mensagem'])
            if st.button(f"Marcar como lido - {alerta['id']}", key=alerta['id']):
                with get_db_connection() as conn:
                    conn.cursor().execute('UPDATE alertas SET lido = TRUE WHERE id = ?', (alerta['id'],))
                st.rerun()
    else:
        st.success("Nenhum alerta pendente!")
