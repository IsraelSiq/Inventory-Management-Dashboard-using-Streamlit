"""
Modulo de importacao em massa de produtos no banco de dados.
"""

import sqlite3
import pandas as pd
from contextlib import contextmanager

@contextmanager
def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
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

def produto_existe(cursor, codigo):
    cursor.execute('SELECT id FROM produtos WHERE codigo = ? AND ativo = TRUE', (codigo,))
    return cursor.fetchone() is not None

def get_produto_id(cursor, codigo):
    cursor.execute('SELECT id FROM produtos WHERE codigo = ? AND ativo = TRUE', (codigo,))
    resultado = cursor.fetchone()
    return resultado['id'] if resultado else None

def inserir_produto(cursor, produto):
    cursor.execute('INSERT INTO produtos (codigo, nome, categoria, unidade_medida, fornecedor, preco_unitario, saldo_atual, estoque_minimo, controla_lote) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (produto.get('ITEM', ''), produto.get('MATERIAL', ''), produto.get('CATEGORIA', 'Outros'), produto.get('UNIDADE', 'UND'), produto.get('FORNECEDOR', ''), float(produto.get('PRECO_UNITARIO', 0.0)), int(produto.get('ESTOQUE_ATUAL', 0)), int(produto.get('ESTOQUE_MINIMO', 10)), produto.get('CONTROLA_LOTE', False)))
    return cursor.lastrowid

def atualizar_produto(cursor, produto_id, produto):
    cursor.execute('UPDATE produtos SET nome = ?, categoria = ?, unidade_medida = ?, fornecedor = ?, preco_unitario = ?, saldo_atual = ?, estoque_minimo = ?, controla_lote = ? WHERE id = ?', (produto.get('MATERIAL', ''), produto.get('CATEGORIA', 'Outros'), produto.get('UNIDADE', 'UND'), produto.get('FORNECEDOR', ''), float(produto.get('PRECO_UNITARIO', 0.0)), int(produto.get('ESTOQUE_ATUAL', 0)), int(produto.get('ESTOQUE_MINIMO', 10)), produto.get('CONTROLA_LOTE', False), produto_id))

def registrar_entrada(cursor, produto_id, quantidade, responsavel='IMPORTACAO', destino='ALMOXARIFADO', custo_unitario=0.0):
    cursor.execute('INSERT INTO movimentacoes (tipo, produto_id, quantidade, responsavel, destino, custo_unitario) VALUES (?, ?, ?, ?, ?, ?)', ('ENTRADA', produto_id, quantidade, responsavel, destino, custo_unitario))

def importar_produtos_em_massa(df_produtos, db_path='cdt_estoque.db', responsavel='IMPORTACAO'):
    relatorio = {'total': len(df_produtos), 'inseridos': 0, 'atualizados': 0, 'erros': 0, 'detalhes': []}
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            for index, row in df_produtos.iterrows():
                produto = row.to_dict()
                codigo = produto.get('ITEM', '')
                try:
                    if not codigo or codigo.strip() == '':
                        relatorio['erros'] += 1
                        relatorio['detalhes'].append({'linha': index + 1, 'erro': 'Codigo vazio', 'produto': produto.get('MATERIAL', 'N/A')})
                        continue
                    if produto_existe(cursor, codigo):
                        produto_id = get_produto_id(cursor, codigo)
                        atualizar_produto(cursor, produto_id, produto)
                        estoque = int(produto.get('ESTOQUE_ATUAL', 0))
                        if estoque > 0: registrar_entrada(cursor, produto_id, estoque, responsavel, 'ALMOXARIFADO', float(produto.get('PRECO_UNITARIO', 0.0)))
                        relatorio['atualizados'] += 1
                        relatorio['detalhes'].append({'linha': index + 1, 'acao': 'ATUALIZADO', 'codigo': codigo, 'produto': produto.get('MATERIAL', 'N/A')})
                    else:
                        produto_id = inserir_produto(cursor, produto)
                        estoque = int(produto.get('ESTOQUE_ATUAL', 0))
                        if estoque > 0: registrar_entrada(cursor, produto_id, estoque, responsavel, 'ALMOXARIFADO', float(produto.get('PRECO_UNITARIO', 0.0)))
                        relatorio['inseridos'] += 1
                        relatorio['detalhes'].append({'linha': index + 1, 'acao': 'INSERIDO', 'codigo': codigo, 'produto': produto.get('MATERIAL', 'N/A')})
                except Exception as e:
                    relatorio['erros'] += 1
                    relatorio['detalhes'].append({'linha': index + 1, 'erro': str(e), 'produto': produto.get('MATERIAL', 'N/A')})
    except Exception as e:
        relatorio['erro_geral'] = str(e)
    return relatorio

def mostrar_relatorio_importacao(relatorio):
    import streamlit as st
    st.subheader("📊 Relatorio da Importacao")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Itens", relatorio.get('total', 0))
    col2.metric("Inseridos", relatorio.get('inseridos', 0), delta_color="normal")
    col3.metric("Atualizados", relatorio.get('atualizados', 0), delta_color="normal")
    col4.metric("Erros", relatorio.get('erros', 0), delta_color="inverse")
    if relatorio.get('detalhes'):
        st.divider()
        st.subheader("📋 Detalhes")
        df_detalhes = pd.DataFrame(relatorio['detalhes'])
        if 'acao' in df_detalhes.columns:
            df_inseridos = df_detalhes[df_detalhes['acao'] == 'INSERIDO']
            df_atualizados = df_detalhes[df_detalhes['acao'] == 'ATUALIZADO']
            if len(df_inseridos) > 0: st.success(f"✅ {len(df_inseridos)} produtos inseridos"); st.dataframe(df_inseridos, use_container_width=True, hide_index=True)
            if len(df_atualizados) > 0: st.info(f"🔄 {len(df_atualizados)} produtos atualizados"); st.dataframe(df_atualizados, use_container_width=True, hide_index=True)
        if 'erro' in df_detalhes.columns:
            df_erros = df_detalhes[df_detalhes['erro'].notna()]
            if len(df_erros) > 0: st.error(f"❌ {len(df_erros)} erros na importacao"); st.dataframe(df_erros, use_container_width=True, hide_index=True)
    if relatorio.get('erro_geral'): st.error(f"❌ Erro geral: {relatorio['erro_geral']}")
