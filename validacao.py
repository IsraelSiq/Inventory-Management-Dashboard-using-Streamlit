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
    if pd.isna(codigo) or str(codigo).strip() == '':
        return ''
    
    codigo = str(codigo).strip()
    
    # Tenta converter pra numero
    try:
        numero = int(float(codigo))
        return f'{numero:03d}'  # 001, 002, etc.
    except:
        # Se nao for numero, retorna como esta (uppercase)
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
    
    categorias_validas = ['MEDICAMENTOS', 'DESCARTAVEIS', 'EQUIPAMENTOS', 'EXAMES', 'OUTROS']
    
    # Tenta encontrar categoria similar
    for cat in categorias_validas:
        if cat in categoria:
            return cat
    
    # Se nao encontrou, retorna 'Outros'
    return 'Outros'


def normalizar_dados(df):
    """
    Normaliza todos os dados do DataFrame.
    
    Args:
        df: DataFrame com dados brutos
    
    Returns:
        DataFrame: Dados normalizados
    """
    df_norm = df.copy()
    
    # Normaliza colunas
    if 'ITEM' in df_norm.columns:
        df_norm['ITEM'] = df_norm['ITEM'].apply(normalizar_codigo)
    
    if 'MATERIAL' in df_norm.columns:
        df_norm['MATERIAL'] = df_norm['MATERIAL'].apply(normalizar_nome)
    
    if 'UNIDADE' in df_norm.columns:
        df_norm['UNIDADE'] = df_norm['UNIDADE'].apply(normalizar_unidade)
    
    if 'CATEGORIA' in df_norm.columns:
        df_norm['CATEGORIA'] = df_norm['CATEGORIA'].apply(normalizar_categoria)
    
    # Converte numeric columns
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
    
    if 'ITEM' not in df.columns:
        return duplicados
    
    # Agrupa por ITEM
    grupos = df.groupby('ITEM')
    
    for codigo, grupo in grupos:
        if len(grupo) > 1:
            duplicados.append({
                'codigo': codigo,
                'quantidade': len(grupo),
                'indices': grupo.index.tolist(),
                'nomes': grupo['MATERIAL'].tolist() if 'MATERIAL' in grupo.columns else []
            })
    
    return duplicados


def validar_codigos_existentes(df, db_path='cdt_estoque.db'):
    """
    Valida se codigos ja existem no banco de dados.
    
    Args:
        df: DataFrame com dados
        db_path: Caminho do banco de dados
    
    Returns:
        list: Lista de codigos que ja existem no banco
    """
    codigos_existentes = []
    
    if 'ITEM' not in df.columns:
        return codigos_existentes
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Pega todos os codigos do banco
        cursor.execute('SELECT codigo FROM produtos WHERE ativo = TRUE')
        codigos_db = set(row[0] for row in cursor.fetchall())
        
        # Verifica quais codigos do DataFrame ja existem
        for codigo in df['ITEM'].unique():
            if codigo and codigo in codigos_db:
                codigos_existentes.append(codigo)
        
        conn.close()
    except Exception as e:
        print(f"Erro ao validar codigos: {e}")
    
    return codigos_existentes


def validar_dados_completos(df, db_path='cdt_estoque.db'):
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
    
    # 1. Valida colunas obrigatorias
    colunas_obrigatorias = ['ITEM', 'MATERIAL', 'UNIDADE', 'ESTOQUE_ATUAL', 'ESTOQUE_MINIMO', 'CATEGORIA']
    colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]
    
    if colunas_faltando:
        erros.append(f"Colunas faltando: {', '.join(colunas_faltando)}")
        return False, erros, avisos
    
    # 2. Valida linhas vazias
    df_valido = df[df['MATERIAL'].notna() & (df['MATERIAL'] != '')]
    
    if len(df_valido) == 0:
        erros.append("Nenhuma linha valida encontrada")
        return False, erros, avisos
    
    # 3. Valida itens sem codigo
    itens_sem_codigo = df_valido[df_valido['ITEM'].isna() | (df_valido['ITEM'] == '')]
    if len(itens_sem_codigo) > 0:
        erros.append(f"{len(itens_sem_codigo)} itens sem codigo")
    
    # 4. Valida itens sem nome
    itens_sem_nome = df_valido[df_valido['MATERIAL'].isna() | (df_valido['MATERIAL'] == '')]
    if len(itens_sem_nome) > 0:
        erros.append(f"{len(itens_sem_nome)} itens sem nome")
    
    # 5. Valida estoque negativo
    if 'ESTOQUE_ATUAL' in df_valido.columns:
        estoque_negativo = df_valido[df_valido['ESTOQUE_ATUAL'] < 0]
        if len(estoque_negativo) > 0:
            erros.append(f"{len(estoque_negativo)} itens com estoque negativo")
    
    # 6. Detecta duplicidades
    duplicados = detectar_duplicidades(df_valido)
    if duplicados:
        for dup in duplicados:
            avisos.append(f"Codigo {dup['codigo']} duplicado {dup['quantidade']} vezes")
    
    # 7. Valida codigos existentes no banco
    codigos_existentes = validar_codigos_existentes(df_valido, db_path)
    if codigos_existentes:
        for codigo in codigos_existentes:
            avisos.append(f"Codigo {codigo} ja existe no banco de dados")
    
    # 8. Estatisticas
    avisos.append(f"Total de itens validos: {len(df_valido)}")
    avisos.append(f"Codigos unicos: {df_valido['ITEM'].nunique()}")
    
    if 'CATEGORIA' in df_valido.columns:
        avisos.append(f"Categorias: {df_valido['CATEGORIA'].nunique()}")
    
    valido = len(erros) == 0
    return valido, erros, avisos
