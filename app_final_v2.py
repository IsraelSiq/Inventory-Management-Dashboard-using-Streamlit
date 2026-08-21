"""
Versao FINAL v2 do app.py com:
- Criar novo material direto na entrada
- Campo de preco removido/oculto
"""

import streamlit as st
import pandas as pd
import sqlite3
from contextlib import contextmanager

from importacao import upload_arquivo, mostrar_previa
from validacao import normalizar_dados, validar_dados_completos
from revisao import mostrar_tabela_revisao, confirmar_selecao, mostrar_resumo
from importacao_em_massa import importar_produtos_em_massa, mostrar_relatorio_importacao

DB_PATH = 'cdt_estoque.db'

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
        cursor.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE NOT NULL, nome TEXT NOT NULL, categoria TEXT NOT NULL, unidade_medida TEXT NOT NULL DEFAULT "unidade", fornecedor TEXT, preco_unitario DECIMAL(10,2) NOT NULL DEFAULT 0, saldo_atual INTEGER NOT NULL DEFAULT 0, estoque_minimo INTEGER NOT NULL DEFAULT 10, controla_lote BOOLEAN NOT NULL DEFAULT FALSE, ativo BOOLEAN NOT NULL DEFAULT TRUE, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        cursor.execute('CREATE TABLE IF NOT EXISTS movimentacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT NOT NULL, produto_id INTEGER NOT NULL, quantidade INTEGER NOT NULL, responsavel TEXT NOT NULL, destino TEXT NOT NULL, custo_unitario DECIMAL(10,2) NOT NULL DEFAULT 0, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        cursor.execute('CREATE TABLE IF NOT EXISTS alertas (id INTEGER PRIMARY KEY AUTOINCREMENT, produto_id INTEGER NOT NULL, tipo TEXT NOT NULL, mensagem TEXT NOT NULL, lido BOOLEAN NOT NULL DEFAULT FALSE, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')

def listar_produtos():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produtos WHERE ativo = TRUE ORDER BY nome')
        return cursor.fetchall()

def cadastrar_produto(codigo, nome, categoria, unidade_medida, fornecedor, preco_unitario, estoque_minimo, controla_lote):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO produtos (codigo, nome, categoria, unidade_medida, fornecedor, preco_unitario, estoque_minimo, controla_lote) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (codigo, nome, categoria, unidade_medida, fornecedor, preco_unitario, estoque_minimo, controla_lote))
        return cursor.lastrowid

def registrar_entrada(produto_id, quantidade, responsavel, destino, custo_unitario):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE produtos SET saldo_atual = saldo_atual + ? WHERE id = ?', (quantidade, produto_id))
        cursor.execute('INSERT INTO movimentacoes (tipo, produto_id, quantidade, responsavel, destino, custo_unitario) VALUES (?, ?, ?, ?, ?, ?)', ('ENTRADA', produto_id, quantidade, responsavel, destino, custo_unitario))
        return cursor.lastrowid

def registrar_saida(produto_id, quantidade, responsavel, destino, custo_unitario):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT saldo_atual FROM produtos WHERE id = ?', (produto_id,))
        produto = cursor.fetchone()
        if not produto or produto['saldo_atual'] < quantidade:
            return None
        cursor.execute('UPDATE produtos SET saldo_atual = saldo_atual - ? WHERE id = ?', (quantidade, produto_id))
        cursor.execute('INSERT INTO movimentacoes (tipo, produto_id, quantidade, responsavel, destino, custo_unitario) VALUES (?, ?, ?, ?, ?, ?)', ('SAIDA', produto_id, quantidade, responsavel, destino, custo_unitario))
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

st.set_page_config(page_title="Controle de Estoque - CDT", layout="wide")
init_database()

st.sidebar.title("🏥 CDT - Controle de Estoque")
menu = st.sidebar.radio("Navegacao", [
    "📊 Dashboard",
    "📦 Produtos",
    "📥 Entradas",
    "📤 Saidas",
    "⚠️ Alertas",
    "📥 Importar Planilha (COMPLETO)"
])

if menu == "📊 Dashboard":
    st.title("📊 Dashboard CDT")
    produtos = listar_produtos()
    if produtos:
        total = len(produtos)
        valor = sum(p['saldo_atual'] * p['preco_unitario'] for p in produtos)
        baixo = sum(1 for p in produtos if p['saldo_atual'] <= p['estoque_minimo'])
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Produtos", total)
        c2.metric("Valor em Estoque", f"R$ {valor:,.2f}")
        c3.metric("Estoque Baixo", baixo)
    else:
        st.info("Nenhum produto cadastrado.")

elif menu == "📦 Produtos":
    st.title("📦 Produtos - CDT")
    with st.form("cadastro_produto"):
        c1, c2, c3 = st.columns(3)
        with c1:
            codigo = st.text_input("Codigo *")
            nome = st.text_input("Nome *")
            categoria = st.selectbox("Categoria *", ["Medicamentos", "Descartaveis", "Equipamentos", "Exames", "Outros"])
        with c2:
            unidade = st.selectbox("Unidade *", ["unidade", "caixa", "pacote", "frasco", "ampola", "seringa", "par", "kit"])
            fornecedor = st.text_input("Fornecedor")
            preco = st.number_input("Preco (R$)", min_value=0.0, step=0.01, value=0.0)  # OPCIONAL
        with c3:
            minimo = st.number_input("Estoque minimo", min_value=0, value=10)
            lote = st.checkbox("Controla lote")
        if st.form_submit_button("Salvar Produto"):
            if codigo and nome:
                try:
                    cadastrar_produto(codigo.upper(), nome, categoria, unidade, fornecedor, preco, minimo, lote)
                    st.success(f"Produto '{nome}' cadastrado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.error("Preencha codigo e nome!")
    st.divider()
    produtos = listar_produtos()
    if produtos:
        df = pd.DataFrame(produtos)
        st.dataframe(df, use_container_width=True, hide_index=True)

# NOVA TELA DE ENTRADAS COM CRIACAO DE NOVO MATERIAL
elif menu == "📥 Entradas":
    st.title("📥 Entradas de Estoque - CDT")
    
    # Inicializa estado para novo produto
    if 'mostrar_novo_produto' not in st.session_state:
        st.session_state.mostrar_novo_produto = False
    
    produtos = listar_produtos()
    
    # Cria dicionario de opcoes
    if produtos:
        opcoes = {f"{p['codigo']} - {p['nome']} (Saldo: {p['saldo_atual']})": p['id'] for p in produtos}
        opcoes_adicionais = {'➕ CRIAR NOVO MATERIAL...': 'NOVO'}
        opcoes_completas = {**opcoes_adicionais, **opcoes}
    else:
        opcoes_completas = {'➕ CRIAR NOVO MATERIAL...': 'NOVO'}
    
    # Selectbox com opcao de criar novo
    with st.form("entrada"):
        c1, c2 = st.columns(2)
        with c1:
            produto_sel = st.selectbox("Produto *", list(opcoes_completas.keys()))
            qtd = st.number_input("Quantidade *", min_value=1, value=1)
        with c2:
            resp = st.text_input("Responsavel *")
            destino = st.selectbox("Destino *", ["Almoxarifado", "Radiologia", "Oftalmologia", "Odontologia", "Nutricao", "Geral"])
        
        # Campo de preco OPCIONAL (oculto por padrao)
        mostrar_preco = st.checkbox("Mostrar campo de preco (opcional)", value=False)
        custo = 0.0
        if mostrar_preco:
            custo = st.number_input("Custo unitario (R$)", min_value=0.0, step=0.01, value=0.0)
        
        if st.form_submit_button("Registrar Entrada"):
            if resp:
                # Verifica se selecionou "CRIAR NOVO"
                if produto_sel == '➕ CRIAR NOVO MATERIAL...':
                    st.session_state.mostrar_novo_produto = True
                    st.rerun()
                else:
                    try:
                        registrar_entrada(opcoes_completas[produto_sel], qtd, resp, destino, custo)
                        st.success("Entrada registrada!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
            else:
                st.error("Preencha o responsavel!")
    
    # Modal de criacao de novo produto
    if st.session_state.mostrar_novo_produto:
        st.divider()
        st.subheader("📦 Cadastrar Novo Material")
        
        with st.form("novo_produto_rapido"):
            c1, c2, c3 = st.columns(3)
            with c1:
                novo_codigo = st.text_input("Codigo *")
                novo_nome = st.text_input("Nome *")
                nova_categoria = st.selectbox("Categoria *", ["Medicamentos", "Descartaveis", "Equipamentos", "Exames", "Outros"])
            with c2:
                nova_unidade = st.selectbox("Unidade *", ["unidade", "caixa", "pacote", "frasco", "ampola", "seringa", "par", "kit"])
                novo_fornecedor = st.text_input("Fornecedor")
                novo_preco = st.number_input("Preco (R$)", min_value=0.0, step=0.01, value=0.0)
            with c3:
                novo_minimo = st.number_input("Estoque minimo", min_value=0, value=10)
                novo_lote = st.checkbox("Controla lote")
            
            c1, c2 = st.columns(2)
            with c1:
                salvar_novo = st.form_submit_button("Salvar e Continuar")
            with c2:
                cancelar = st.form_submit_button("Cancelar")
            
            if salvar_novo:
                if novo_codigo and novo_nome:
                    try:
                        novo_id = cadastrar_produto(novo_codigo.upper(), novo_nome, nova_categoria, nova_unidade, novo_fornecedor, novo_preco, novo_minimo, novo_lote)
                        st.success(f"Produto '{novo_nome}' cadastrado!")
                        st.session_state.mostrar_novo_produto = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
                else:
                    st.error("Preencha codigo e nome!")
            
            if cancelar:
                st.session_state.mostrar_novo_produto = False
                st.rerun()
    
    # Rodape
    if not produtos:
        st.info("Nenhum produto cadastrado. Clique em '➕ CRIAR NOVO MATERIAL...' para cadastrar.")

elif menu == "📤 Saidas":
    st.title("📤 Saidas de Estoque - CDT")
    produtos = listar_produtos()
    if produtos:
        opcoes = {f"{p['codigo']} - {p['nome']} (Saldo: {p['saldo_atual']})": p['id'] for p in produtos}
        with st.form("saida"):
            c1, c2 = st.columns(2)
            with c1:
                produto_sel = st.selectbox("Produto *", list(opcoes.keys()))
                qtd = st.number_input("Quantidade *", min_value=1, value=1)
            with c2:
                resp = st.text_input("Responsavel *")
                destino = st.selectbox("Destino *", ["Almoxarifado", "Radiologia", "Oftalmologia", "Odontologia", "Nutricao", "Geral"])
            
            # Campo de preco OPCIONAL
            mostrar_preco = st.checkbox("Mostrar campo de preco (opcional)", value=False)
            custo = 0.0
            if mostrar_preco:
                custo = st.number_input("Custo unitario (R$)", min_value=0.0, step=0.01, value=0.0)
            
            if st.form_submit_button("Registrar Saida"):
                if resp:
                    resultado = registrar_saida(opcoes[produto_sel], qtd, resp, destino, custo)
                    if resultado:
                        st.success("Saida registrada!")
                        st.rerun()
                else:
                    st.error("Preencha o responsavel!")
    else:
        st.info("Nenhum produto cadastrado.")

elif menu == "⚠️ Alertas":
    st.title("⚠️ Alertas de Estoque Baixo - CDT")
    verificar_alertas()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT a.*, p.nome as produto_nome FROM alertas a JOIN produtos p ON a.produto_id = p.id WHERE a.lido = FALSE ORDER BY a.criado_em DESC')
        alertas = cursor.fetchall()
    if alertas:
        for alerta in alertas:
            st.error(alerta['mensagem'])
            if st.button(f"Marcar como lido", key=f"alert_{alerta['id']}"):
                with get_db_connection() as conn:
                    conn.cursor().execute('UPDATE alertas SET lido = TRUE WHERE id = ?', (alerta['id'],))
                st.rerun()
    else:
        st.success("✅ Nenhum alerta pendente!")

# TELA DE IMPORTACAO
elif menu == "📥 Importar Planilha (COMPLETO)":
    st.title("📥 Importar Planilha de Estoque")
    st.markdown("Importe produtos em massa com revisao, validacao e confirmacao.")
    
    # Inicializa estado da sessao
    if 'df_importacao' not in st.session_state:
        st.session_state.df_importacao = None
    if 'df_revisao' not in st.session_state:
        st.session_state.df_revisao = None
    if 'importacao_concluida' not in st.session_state:
        st.session_state.importacao_concluida = False
    
    # Passo 1: Upload
    st.subheader("📤 Passo 1: Upload do Arquivo")
    df, abas = upload_arquivo()
    
    if df is not None:
        st.session_state.df_importacao = df
        
        # Passo 2: Normaliza
        st.subheader("🔄 Passo 2: Normalizacao")
        df_norm = normalizar_dados(df)
        st.success("✅ Dados normalizados!")
        
        # Passo 3: Valida
        st.subheader("✅ Passo 3: Validacao")
        valido, erros, avisos = validar_dados_completos(df_norm, DB_PATH)
        
        if not valido:
            st.error("❌ Erros encontrados:")
            for erro in erros:
                st.error(f"  • {erro}")
            st.stop()
        
        st.success("✅ Dados validos!")
        
        # Passo 4: Revisao
        st.divider()
        st.subheader("📋 Passo 4: Revisao dos Itens")
        df_editado = mostrar_tabela_revisao(df_norm)
        
        if df_editado is not None and len(df_editado) > 0:
            st.session_state.df_revisao = df_editado
            
            # Passo 5: Confirma selecao
            st.divider()
            st.subheader("✅ Passo 5: Confirmacao")
            
            df_selecionados, resumo = confirmar_selecao(df_editado)
            
            # Mostra resumo
            mostrar_resumo(resumo)
            
            # Botao de confirmacao
            if resumo['selecionados'] > 0:
                if st.button(f"🚀 CONFIRMAR IMPORTACAO DE {resumo['selecionados']} ITENS", type="primary", disabled=st.session_state.importacao_concluida):
                    with st.spinner("⏳ Importando produtos..."):
                        # Remove coluna 'selecionado' se existir
                        if 'selecionado' in df_selecionados.columns:
                            df_selecionados = df_selecionados.drop(columns=['selecionado'])
                        
                        # Importa em massa
                        relatorio = importar_produtos_em_massa(df_selecionados, DB_PATH, responsavel='IMPORTACAO')
                        
                        # Mostra relatorio
                        mostrar_relatorio_importacao(relatorio)
                        
                        # Sucesso
                        if relatorio['erros'] == 0:
                            st.success(f"🎉 IMPORTACAO CONCLUIDA COM SUCESSO!")
                            st.balloons()
                            st.session_state.importacao_concluida = True
                        else:
                            st.warning(f"⚠️ Importacao concluida com {relatorio['erros']} erros")
            else:
                st.warning("⚠️ Nenhum item selecionado para importacao")
