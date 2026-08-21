import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

import app


def test_produto_com_lote_exige_lote_e_validade(tmp_path, monkeypatch):
    db_path = tmp_path / 'estoque.db'
    monkeypatch.setattr(app, 'DB_PATH', str(db_path))
    app.init_database()

    with pytest.raises(ValueError, match='Lote e obrigatorio'):
        app.cadastrar_produto(
            codigo='L001',
            nome='Kit de teste',
            categoria='Descartaveis',
            unidade_medida='unidade',
            fornecedor='A',
            preco_unitario=5.0,
            estoque_minimo=1,
            controla_lote=True,
            lote='',
            validade='2026-12-31',
        )


def test_entrada_com_lote_valido_grava_metadata(tmp_path, monkeypatch):
    db_path = tmp_path / 'estoque.db'
    monkeypatch.setattr(app, 'DB_PATH', str(db_path))
    app.init_database()

    produto_id = app.cadastrar_produto(
        codigo='L002',
        nome='Seringa',
        categoria='Descartaveis',
        unidade_medida='unidade',
        fornecedor='A',
        preco_unitario=3.0,
        estoque_minimo=1,
        controla_lote=True,
        lote='LT-03',
        validade='2026-12-31',
    )

    app.registrar_entrada(
        produto_id,
        25,
        'Operador',
        'Almoxarifado',
        3.0,
        lote='LT-03',
        validade='2026-12-31'
    )

    movimentacoes = app.listar_movimentacoes()
    assert movimentacoes[0]['lote'] == 'LT-03'
    assert movimentacoes[0]['validade'] == '2026-12-31'
