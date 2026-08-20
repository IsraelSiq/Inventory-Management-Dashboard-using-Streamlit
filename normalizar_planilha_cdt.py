"""
Script para normalizar planilha de estoque do CDT.

Uso: python normalizar_planilha_cdt.py

Entrada: CONTROLE-DE-ESTOQUE-ATUALIZADO-JULHO-2026.xlsx
Saida: cdt_estoque_normalizado.xlsx, cdt_estoque_normalizado.csv
"""

import pandas as pd
import re


def extrair_numero(texto):
    """Extrai numero de string. Ex: '7 PCT' -> 7, '1+10' -> 11"""
    if pd.isna(texto) or texto == '':
        return 0
    numeros = re.findall(r'\d+', str(texto))
    return sum(int(n) for n in numeros) if numeros else 0


def normalizar_unidade(unidade):
    """Normaliza unidade: UNID->UND, CX->CAIXA, PCT->PACOTE"""
    if pd.isna(unidade):
        return 'UND'
    mapeamento = {'UND': 'UND', 'UNID': 'UND', 'CX': 'CAIXA', 'PCT': 'PACOTE', 'KIT': 'KIT'}
    return mapeamento.get(str(unidade).strip().upper(), 'UND')


def normalizar_codigo(item):
    """Normaliza codigo: '1.0' -> '001', '25.0' -> '025'"""
    if pd.isna(item):
        return ''
    try:
        return f'{int(float(str(item).strip())):03d}'
    except:
        return str(item).strip()


def inferir_categoria(nome):
    """Infere categoria do produto."""
    if pd.isna(nome):
        return 'Outros'
    nome = str(nome).upper()
    if any(x in nome for x in ['CREME', 'AMPOLA', 'COMPRIMIDO', 'MG', 'ML']):
        return 'Medicamentos'
    if any(x in nome for x in ['AGULHA', 'SERINGA', 'LUVA', 'GAZE', 'ALGODAO']):
        return 'Descartaveis'
    if any(x in nome for x in ['ESFIGMOMANOMETRO', 'ESTETOSCOPIO', 'TERMOMETRO']):
        return 'Equipamentos'
    return 'Outros'


def normalizar_planilha(arquivo_entrada, saida_xlsx, saida_csv):
    """Normaliza planilha do CDT."""
    print(f"Lendo: {arquivo_entrada}")
    df = pd.read_excel(arquivo_entrada, sheet_name='PLANILHA ATUALIZADA 01.07.2026', header=3)
    
    df_norm = pd.DataFrame()
    df_norm['ITEM'] = df['ITEM'].apply(normalizar_codigo)
    df_norm['MATERIAL'] = df.iloc[:, 1].fillna('').str.strip()
    df_norm['UNIDADE'] = df.iloc[:, 2].apply(normalizar_unidade)
    df_norm['ESTOQUE_ATUAL'] = df.iloc[:, 4].apply(extrair_numero)
    df_norm['ESTOQUE_MINIMO'] = df_norm['ESTOQUE_ATUAL'].apply(lambda x: max(5, int(x * 0.1)))
    df_norm['FORNECEDOR'] = ''
    df_norm['PRECO_UNITARIO'] = 0.0
    df_norm['CATEGORIA'] = df_norm['MATERIAL'].apply(inferir_categoria)
    
    df_norm = df_norm[df_norm['MATERIAL'] != '']
    df_norm = df_norm.drop_duplicates(subset=['ITEM'])
    df_norm = df_norm.sort_values('ITEM')
    
    df_norm.to_excel(saida_xlsx, index=False)
    df_norm.to_csv(saida_csv, index=False, encoding='utf-8-sig')
    
    print(f"Normalizados: {len(df_norm)} produtos")
    return df_norm


if __name__ == '__main__':
    df = normalizar_planilha('CONTROLE-DE-ESTOQUE-ATUALIZADO-JULHO-2026.xlsx',
                              'cdt_estoque_normalizado.xlsx',
                              'cdt_estoque_normalizado.csv')
    print(f"\nCategorias: {df['CATEGORIA'].value_counts().to_dict()}")
    print(df.head(10).to_string())
