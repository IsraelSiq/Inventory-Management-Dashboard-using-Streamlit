import os

from app import (
    init_database,
    cadastrar_produto,
    registrar_entrada,
    registrar_saida,
    listar_produtos,
    get_db_connection,
)


def limpar_banco():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clinica_estoque.db')
    if os.path.exists(db_path):
        os.remove(db_path)


def testar_fluxo_basico():
    limpar_banco()
    init_database()

    produto_id = cadastrar_produto(
        codigo='A100',
        nome='Seringa 5ml',
        categoria='Descartaveis',
        unidade_medida='unidade',
        fornecedor='Fornecedor Teste',
        preco_unitario=12.5,
        estoque_minimo=5,
        controla_lote=False,
    )
    assert produto_id is not None

    registrar_entrada(produto_id, 10, 'Operador', 'Almoxarifado', 12.5)
    registrar_saida(produto_id, 3, 'Operador', 'Geral', 12.5)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT saldo_atual FROM produtos WHERE id = ?', (produto_id,))
        saldo = cursor.fetchone()['saldo_atual']

    assert saldo == 7, f'Saldo inesperado: {saldo}'
    produtos = listar_produtos()
    assert len(produtos) == 1, f'Quantidade de produtos inesperada: {len(produtos)}'

    print('Smoke test concluído com sucesso: cadastro, entrada, saída e saldo final validados.')


if __name__ == '__main__':
    testar_fluxo_basico()
