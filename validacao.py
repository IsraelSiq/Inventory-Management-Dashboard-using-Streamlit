"""
Modulo de validacao e normalizacao de dados para importacao em massa.

Funcoes:
- normalizar_dados(df) -> DataFrame normalizado
- detectar_duplicidades(df) -> lista de duplicados
- validar_codigos_existentes(df, db_path) -> lista de codigos ja existentes
- validar_dados_completos(df, db_path) -> (valido, erros, avisos)
"""

import pandas as pd
import sqlite3


def normalizar_codigo(codigo):
    """
    Normaliza codigo para formato padrao.
    Ex: '1.0' -> '001', '25' -> '025', 'ABC' -> 'ABC'
    """
    if pd.isna(codigo):
        return ''

    codigo = str(codigo).strip()
    if codigo == '':
        return ''

    try:
        numero = int(float(codigo))
        return f'{numero:03d}'
    except (TypeError, ValueError):
        return codigo.upper()


def normalizar_unidade(unidade):
    """
    Normaliza unidade para padrao do sistema.
    """
    if pd.isna(unidade):
        return 'UND'
    
    unidade = str(unidade).strip().upper()
    
    # Mapeamento de unidades
    mapeamento = {
        'UND': 'UND',
        'UNID': 'UND',
        'UNIDADE': 'UND',
        'CX': 'CAIXA',
        'CAIXA': 'CAIXA',
        'PCT': 'PACOTE',
        'PACOTE': 'PACOTE',
        'KIT': 'KIT',
        'FRASCO': 'FRASCO',
        'AMPOLA': 'AMPOLA',
        'PAR': 'PAR',
        'SERINGA': 'SERINGA',
        'COMPRIMIDO': 'COMPRIMIDO',
        'ML': 'ML',
        'G': 'G',
        'KG': 'KG'
    }
    
    return mapeamento.get(unidade, 'UND')


def normalizar_nome(nome):
    """
    Normaliza nome do produto.
    """
    if pd.isna(nome):
        return ''
    
    # Remove espacos extras e converte pra uppercase
    nome = str(nome).strip()
    nome = ' '.join(nome.split())  # Remove espacos duplicados
    
    return nome.upper()


def normalizar_categoria(categoria):
    """
    Normaliza categoria para valores validos.
    """
    if pd.isna(categoria):
        return 'Outros'

    categoria = str(categoria).strip().upper()
    mapeamento = {
        'MEDICAMENTOS': 'Medicamentos',
        'DESCARTAVEIS': 'Descartaveis',
        'EQUIPAMENTOS': 'Equipamentos',
        'EXAMES': 'Exames',
        'OUTROS': 'Outros',
    }

    for chave, valor in mapeamento.items():
        if chave in categoria:
            return valor

    return 'Outros'


def normalizar_dados(df):
    """
    Normaliza todos os dados do DataFrame.
    
    Args:
        df: DataFrame com dados brutos
    
    Returns:
        DataFrame: Dados normalizados
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df_norm = df.copy()

    if 'ITEM' in df_norm.columns:
        df_norm['ITEM'] = df_norm['ITEM'].apply(normalizar_codigo)

    if 'MATERIAL' in df_norm.columns:
        df_norm['MATERIAL'] = df_norm['MATERIAL'].apply(normalizar_nome)

    if 'UNIDADE' in df_norm.columns:
        df_norm['UNIDADE'] = df_norm['UNIDADE'].apply(normalizar_unidade)

    if 'CATEGORIA' in df_norm.columns:
        df_norm['CATEGORIA'] = df_norm['CATEGORIA'].apply(normalizar_categoria)

    if 'ESTOQUE_ATUAL' in df_norm.columns:
        df_norm['ESTOQUE_ATUAL'] = pd.to_numeric(df_norm['ESTOQUE_ATUAL'], errors='coerce').fillna(0).astype(int)

    if 'ESTOQUE_MINIMO' in df_norm.columns:
        df_norm['ESTOQUE_MINIMO'] = pd.to_numeric(df_norm['ESTOQUE_MINIMO'], errors='coerce').fillna(10).astype(int)

    if 'PRECO_UNITARIO' in df_norm.columns:
        df_norm['PRECO_UNITARIO'] = pd.to_numeric(df_norm['PRECO_UNITARIO'], errors='coerce').fillna(0.0)

    return df_norm


def detectar_duplicidades(df):
    """
    Detecta itens duplicados no DataFrame.
    
    Args:
        df: DataFrame com dados
    
    Returns:
        list: Lista de dicionarios com informacoes dos duplicados
    """
    duplicados = []

    if df is None or 'ITEM' not in df.columns:
        return duplicados

    df_dup = df.copy()
    df_dup['ITEM'] = df_dup['ITEM'].astype(str).str.strip()
    df_dup = df_dup[df_dup['ITEM'] != '']

    grupos = df_dup.groupby('ITEM')

    for codigo, grupo in grupos:
        if len(grupo) > 1:
            duplicados.append({
                'codigo': codigo,
                'quantidade': len(grupo),
                'indices': grupo.index.tolist(),
                'nomes': grupo['MATERIAL'].tolist() if 'MATERIAL' in grupo.columns else []
            })

    return duplicados


def validar_codigos_existentes(df, db_path='clinica_estoque.db'):
    """
    Valida se codigos ja existem no banco de dados.
    
    Args:
        df: DataFrame com dados
        db_path: Caminho do banco de dados
    
    Returns:
        list: Lista de codigos que ja existem no banco
    """
    codigos_existentes = []

    if df is None or 'ITEM' not in df.columns:
        return codigos_existentes

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT codigo FROM produtos WHERE ativo = TRUE')
        codigos_db = {str(row[0]).strip().upper() for row in cursor.fetchall() if row and row[0] is not None}

        for codigo in df['ITEM'].dropna().astype(str):
            codigo_normalizado = codigo.strip().upper()
            if codigo_normalizado and codigo_normalizado in codigos_db:
                codigos_existentes.append(codigo_normalizado)

        conn.close()
    except Exception as e:
        print(f"Erro ao validar codigos: {e}")

    return codigos_existentes


def validar_dados_completos(df, db_path='clinica_estoque.db'):
    """
    Valida dados completos e retorna erros e avisos.
    
    Args:
        df: DataFrame com dados
        db_path: Caminho do banco de dados
    
    Returns:
        tuple: (valido, erros, avisos)
    """
    erros = []
    avisos = []

    if df is None or df.empty:
        erros.append('Arquivo vazio')
        return False, erros, avisos

    colunas_obrigatorias = ['ITEM', 'MATERIAL', 'UNIDADE', 'ESTOQUE_ATUAL', 'ESTOQUE_MINIMO', 'CATEGORIA']
    colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]

    if colunas_faltando:
        erros.append(f"Colunas faltando: {', '.join(colunas_faltando)}")
        return False, erros, avisos

    df_valido = df.copy()
    df_valido['ITEM'] = df_valido['ITEM'].apply(lambda v: str(v).strip() if not pd.isna(v) else '')
    df_valido['MATERIAL'] = df_valido['MATERIAL'].apply(lambda v: str(v).strip() if not pd.isna(v) else '')

    df_valido = df_valido[df_valido['MATERIAL'] != '']

    if len(df_valido) == 0:
        erros.append('Nenhuma linha valida encontrada')
        return False, erros, avisos

    itens_sem_codigo = df_valido[df_valido['ITEM'].isna() | (df_valido['ITEM'] == '')]
    if len(itens_sem_codigo) > 0:
        erros.append(f"{len(itens_sem_codigo)} itens sem codigo")

    itens_sem_nome = df_valido[df_valido['MATERIAL'].isna() | (df_valido['MATERIAL'] == '')]
    if len(itens_sem_nome) > 0:
        erros.append(f"{len(itens_sem_nome)} itens sem nome")

    if 'ESTOQUE_ATUAL' in df_valido.columns:
        estoque_negativo = pd.to_numeric(df_valido['ESTOQUE_ATUAL'], errors='coerce').lt(0)
        if estoque_negativo.any():
            erros.append(f"{int(estoque_negativo.sum())} itens com estoque negativo")

    if 'ESTOQUE_MINIMO' in df_valido.columns:
        estoque_minimo_negativo = pd.to_numeric(df_valido['ESTOQUE_MINIMO'], errors='coerce').lt(0)
        if estoque_minimo_negativo.any():
            erros.append(f"{int(estoque_minimo_negativo.sum())} itens com estoque minimo negativo")

    if 'PRECO_UNITARIO' in df_valido.columns:
        preco_negativo = pd.to_numeric(df_valido['PRECO_UNITARIO'], errors='coerce').lt(0)
        if preco_negativo.any():
            erros.append(f"{int(preco_negativo.sum())} itens com preco unitario negativo")

    if 'UNIDADE' in df_valido.columns:
        unidades_vazias = df_valido['UNIDADE'].fillna('').astype(str).str.strip().eq('')
        if unidades_vazias.any():
            erros.append(f"{int(unidades_vazias.sum())} itens com unidade vazia")

    if 'CATEGORIA' in df_valido.columns:
        categorias_vazias = df_valido['CATEGORIA'].fillna('').astype(str).str.strip().eq('')
        if categorias_vazias.any():
            erros.append(f"{int(categorias_vazias.sum())} itens com categoria vazia")

    duplicados = detectar_duplicidades(df_valido)
    if duplicados:
        for dup in duplicados:
            avisos.append(f"Codigo {dup['codigo']} duplicado {dup['quantidade']} vezes")

    codigos_existentes = validar_codigos_existentes(df_valido, db_path)
    if codigos_existentes:
        for codigo in sorted(set(codigos_existentes)):
            avisos.append(f"Codigo {codigo} ja existe no banco de dados")

    avisos.append(f"Total de itens validos: {len(df_valido)}")
    avisos.append(f"Codigos unicos: {df_valido['ITEM'].nunique()}")

    if 'CATEGORIA' in df_valido.columns:
        avisos.append(f"Categorias: {df_valido['CATEGORIA'].nunique()}")

    valido = len(erros) == 0
    return valido, erros, avisos
