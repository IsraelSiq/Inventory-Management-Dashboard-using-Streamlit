"""
Modulo de leitura e validacao de arquivos para importacao em massa.
"""

import pandas as pd
import streamlit as st

COLUNAS_OBRIGATORIAS = ['ITEM', 'MATERIAL', 'UNIDADE', 'ESTOQUE_ATUAL', 'ESTOQUE_MINIMO', 'CATEGORIA']

def ler_arquivo(caminho):
    if caminho.endswith('.csv'):
        df = pd.read_csv(caminho, encoding='utf-8-sig')
        return df, None
    elif caminho.endswith('.xlsx'):
        abas_dict = pd.read_excel(caminho, sheet_name=None)
        abas = list(abas_dict.keys())
        df = abas_dict[abas[0]]
        return df, abas
    else:
        raise ValueError(f"Formato nao suportado: {caminho}")

def validar_colunas(df):
    erros = []
    colunas_faltando = [col for col in COLUNAS_OBRIGATORIAS if col not in df.columns]
    if colunas_faltando:
        erros.append(f"Colunas faltando: {', '.join(colunas_faltando)}")
    if len(df) == 0:
        erros.append("Arquivo vazio")
    if 'ITEM' in df.columns and df['ITEM'].isna().sum() > 0:
        erros.append(f"{df['ITEM'].isna().sum()} itens sem codigo")
    if 'MATERIAL' in df.columns and df['MATERIAL'].isna().sum() > 0:
        erros.append(f"{df['MATERIAL'].isna().sum()} itens sem nome")
    return len(erros) == 0, erros

def extrair_dados(df):
    dados = []
    for idx, row in df.iterrows():
        produto = {
            'item': str(row.get('ITEM', '')).strip(),
            'material': str(row.get('MATERIAL', '')).strip(),
            'unidade': str(row.get('UNIDADE', 'UND')).strip().upper(),
            'estoque_atual': int(row.get('ESTOQUE_ATUAL', 0)),
            'estoque_minimo': int(row.get('ESTOQUE_MINIMO', 10)),
            'fornecedor': str(row.get('FORNECEDOR', '')).strip(),
            'preco_unitario': float(row.get('PRECO_UNITARIO', 0.0)),
            'categoria': str(row.get('CATEGORIA', 'Outros')).strip()
        }
        dados.append(produto)
    return dados

def upload_arquivo():
    st.subheader("📁 Upload de Arquivo")
    arquivo = st.file_uploader(
        "Selecione o arquivo Excel ou CSV",
        type=['xlsx', 'csv'],
        help="Use o template oficial TEMPLATE_IMPORTACAO_CDT.xlsx"
    )
    if arquivo is None:
        return None, None
    try:
        if arquivo.name.endswith('.csv'):
            df = pd.read_csv(arquivo, encoding='utf-8-sig')
            abas = None
        else:
            abas_dict = pd.read_excel(arquivo, sheet_name=None)
            abas = list(abas_dict.keys())
            df = abas_dict[abas[0]]
        st.success(f"✅ Arquivo carregado: {arquivo.name}")
        st.info(f"📊 {len(df)} linhas | {len(df.columns)} colunas")
        if abas:
            st.info(f"📑 Abas disponiveis: {', '.join(abas)}")
        return df, abas
    except Exception as e:
        st.error(f"❌ Erro ao ler arquivo: {str(e)}")
        return None, None

def mostrar_previa(df, linhas=10):
    st.subheader("📋 Previa dos Dados")
    if df is None or len(df) == 0:
        st.warning("Nenhum dado para mostrar")
        return
    st.dataframe(df.head(linhas), use_container_width=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Linhas", len(df))
    col2.metric("Colunas", len(df.columns))
    col3.metric("Linhas com Dados", len(df[df['MATERIAL'].notna()]) if 'MATERIAL' in df.columns else 0)

def validar_dados(df):
    st.subheader("✅ Validacao")
    valido, erros = validar_colunas(df)
    if valido:
        st.success("✅ Arquivo valido! Todas as colunas obrigatorias presentes.")
        col1, col2 = st.columns(2)
        if 'CATEGORIA' in df.columns:
            col1.metric("Categorias", df['CATEGORIA'].nunique())
        if 'UNIDADE' in df.columns:
            col2.metric("Unicas", df['UNIDADE'].nunique())
        return True
    else:
        st.error("❌ Erros encontrados:")
        for erro in erros:
            st.error(f"  • {erro}")
        return False

if __name__ == '__main__':
    print("Testando modulo importacao...")
    df_teste = pd.DataFrame({
        'ITEM': ['001', '002', '003'],
        'MATERIAL': ['Produto A', 'Produto B', 'Produto C'],
        'UNIDADE': ['UND', 'UND', 'PCT'],
        'ESTOQUE_ATUAL': [100, 50, 200],
        'ESTOQUE_MINIMO': [10, 5, 20],
        'CATEGORIA': ['Medicamentos', 'Descartaveis', 'Descartaveis']
    })
    valido, erros = validar_colunas(df_teste)
    print(f"Valido: {valido}")
    print(f"Erros: {erros}")
    dados = extrair_dados(df_teste)
    print(f"Dados extraidos: {len(dados)}")
    print(dados[0])
    print("\n✅ Testes concluidos!")
