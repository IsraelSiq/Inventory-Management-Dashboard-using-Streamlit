import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import app


def test_permissoes_do_papel_admin():
    assert app.usuario_tem_permissao('produtos', 'admin') is True
    assert app.usuario_tem_permissao('entradas', 'admin') is True
    assert app.usuario_tem_permissao('relatorios', 'admin') is True


def test_permissoes_do_papel_operador():
    assert app.usuario_tem_permissao('entradas', 'operador') is True
    assert app.usuario_tem_permissao('saidas', 'operador') is True
    assert app.usuario_tem_permissao('produtos', 'operador') is False


def test_permissoes_do_papel_visualizacao():
    assert app.usuario_tem_permissao('dashboard', 'visualizacao') is True
    assert app.usuario_tem_permissao('relatorios', 'visualizacao') is True
    assert app.usuario_tem_permissao('produtos', 'visualizacao') is False
