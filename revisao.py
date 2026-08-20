"""
Modulo de revisao e confirmacao de dados para importacao em massa.

Funcoes:
- mostrar_tabela_revisao(df) -> DataFrame com selecao
- editar_item(item) -> item editado
- confirmar_selecao(df_selecao) -> lista de itens selecionados
"""

import streamlit as st
import pandas as pd


def mostrar_tabela_revisao(df):
    """
    Mostra tabela de revisao com checkbox para cada item.
    
    Args:
        df: DataFrame com dados normalizados
    
    Returns:
        DataFrame: Dados com coluna 'selecionado'
    """
    st.subheader("📋 Revisao dos Itens")
    
    if df is None or len(df) == 0:
        st.warning("Nenhum item para revisar")
        return pd.DataFrame()
    
    # Cria coluna de selecao
    df_revisao = df.copy()
    df_revisao['selecionado'] = True
    
    # Mostra estatisticas
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Itens", len(df_revisao))
    col2.metric("Selecionados", df_revisao['selecionado'].sum())
    col3.metric("Ignorados", len(df_revisao) - df_revisao['selecionado'].sum())
    
    # Mostra tabela editavel
    st.info("💡 Dica: Use os checkboxes para selecionar/deselecionar itens")
    
    # Configura colunas para exibicao
    colunas_exibicao = ['ITEM', 'MATERIAL', 'UNIDADE', 'ESTOQUE_ATUAL', 'ESTOQUE_MINIMO', 'CATEGORIA']
    colunas_exibicao = [col for col in colunas_exibicao if col in df_revisao.columns]
    
    # Mostra tabela com editor
    df_editado = st.data_editor(
        df_revisao[colunas_exibicao + ['selecionado']],
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "selecionado": st.column_config.CheckboxColumn(
                "Selecionar",
                help="Selecionar item para importacao",
                default=True,
            ),
            "ITEM": st.column_config.TextColumn("Codigo", width="small"),
            "MATERIAL": st.column_config.TextColumn("Material", width="medium"),
            "UNIDADE": st.column_config.TextColumn("Unidade", width="small"),
            "ESTOQUE_ATUAL": st.column_config.NumberColumn("Estoque Atual", width="small"),
            "ESTOQUE_MINIMO": st.column_config.NumberColumn("Estoque Min", width="small"),
            "CATEGORIA": st.column_config.TextColumn("Categoria", width="small"),
        }
    )
    
    return df_editado


def editar_item(item, key_prefix="edit"):
    """
    Mostra formulario para editar um item.
    
    Args:
        item: Dicionario com dados do item
        key_prefix: Prefixo para chaves dos widgets
    
    Returns:
        dict: Item editado
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        item['ITEM'] = st.text_input("Codigo", value=item.get('ITEM', ''), key=f"{key_prefix}_codigo")
        item['MATERIAL'] = st.text_input("Material", value=item.get('MATERIAL', ''), key=f"{key_prefix}_material")
        item['UNIDADE'] = st.selectbox(
            "Unidade",
            options=['UND', 'CAIXA', 'PACOTE', 'KIT', 'FRASCO', 'AMPOLA', 'PAR', 'SERINGA'],
            index=0 if item.get('UNIDADE', 'UND') == 'UND' else 0,
            key=f"{key_prefix}_unidade"
        )
    
    with col2:
        item['ESTOQUE_ATUAL'] = st.number_input("Estoque Atual", min_value=0, value=int(item.get('ESTOQUE_ATUAL', 0)), key=f"{key_prefix}_estoque")
        item['ESTOQUE_MINIMO'] = st.number_input("Estoque Minimo", min_value=0, value=int(item.get('ESTOQUE_MINIMO', 10)), key=f"{key_prefix}_minimo")
        item['CATEGORIA'] = st.selectbox(
            "Categoria",
            options=['Medicamentos', 'Descartaveis', 'Equipamentos', 'Exames', 'Outros'],
            index=0,
            key=f"{key_prefix}_categoria"
        )
    
    with col3:
        item['FORNECEDOR'] = st.text_input("Fornecedor", value=item.get('FORNECEDOR', ''), key=f"{key_prefix}_fornecedor")
        item['PRECO_UNITARIO'] = st.number_input("Preco (R$)", min_value=0.0, step=0.01, value=float(item.get('PRECO_UNITARIO', 0.0)), key=f"{key_prefix}_preco")
        selecionado = st.checkbox("Importar", value=True, key=f"{key_prefix}_selecionado")
    
    return item, selecionado


def confirmar_selecao(df_editado):
    """
    Confirma selecao e retorna lista de itens selecionados.
    
    Args:
        df_editado: DataFrame editado com coluna 'selecionado'
    
    Returns:
        tuple: (df_selecionados, resumo)
    """
    if df_editado is None or len(df_editado) == 0:
        return pd.DataFrame(), {}
    
    # Filtra itens selecionados
    df_selecionados = df_editado[df_editado['selecionado'] == True].copy()
    
    # Remove coluna de selecao
    if 'selecionado' in df_selecionados.columns:
        df_selecionados = df_selecionados.drop(columns=['selecionado'])
    
    # Cria resumo
    resumo = {
        'total': len(df_editado),
        'selecionados': len(df_selecionados),
        'ignorados': len(df_editado) - len(df_selecionados),
        'categorias': df_selecionados['CATEGORIA'].nunique() if 'CATEGORIA' in df_selecionados.columns else 0,
        'unidades': df_selecionados['UNIDADE'].nunique() if 'UNIDADE' in df_selecionados.columns else 0
    }
    
    return df_selecionados, resumo


def mostrar_resumo(resumo):
    """
    Mostra resumo da selecao.
    
    Args:
        resumo: Dicionario com estatisticas
    """
    st.subheader("📊 Resumo")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Itens", resumo.get('total', 0))
    col2.metric("Selecionados", resumo.get('selecionados', 0), delta_color="normal")
    col3.metric("Ignorados", resumo.get('ignorados', 0), delta_color="inverse")
    col4.metric("Categorias", resumo.get('categorias', 0))
    
    # Barra de progresso
    progresso = resumo.get('selecionados', 0) / max(resumo.get('total', 1), 1)
    st.progress(progresso, text=f"{int(progresso * 100)}% selecionados")
