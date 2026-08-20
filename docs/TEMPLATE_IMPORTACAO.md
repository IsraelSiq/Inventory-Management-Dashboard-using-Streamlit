# Template de Importacao de Estoque - CDT

Este diretorio contem os arquivos para importacao em massa de produtos do CDT.

## Arquivos

- `TEMPLATE_IMPORTACAO_CDT.xlsx` - Template oficial em Excel
- `TEMPLATE_IMPORTACAO_CDT.csv` - Template oficial em CSV
- `normalizar_planilha_cdt.py` - Script Python para normalizar planilha original

## Colunas do Template

| Coluna | Tipo | Obrigatoria | Descricao |
|--------|------|-------------|------------|
| `ITEM` | Texto | Sim | Codigo do produto (ex: 001, 002, 003) |
| `MATERIAL` | Texto | Sim | Descricao completa do produto |
| `UNIDADE` | Texto | Sim | Unidade de medida (UND, CAIXA, PACOTE, KIT, etc.) |
| `ESTOQUE_ATUAL` | Numero | Sim | Quantidade atual em estoque |
| `ESTOQUE_MINIMO` | Numero | Sim | Quantidade minima para alerta |
| `FORNECEDOR` | Texto | Nao | Nome do fornecedor |
| `PRECO_UNITARIO` | Numero | Nao | Preco unitario (R$) |
| `CATEGORIA` | Texto | Sim | Categoria (Medicamentos, Descartaveis, Equipamentos, Exames, Outros) |

## Categorias Validas

- `Medicamentos`
- `Descartaveis`
- `Equipamentos`
- `Exames`
- `Outros`

## Exemplo de Preenchimento

| ITEM | MATERIAL | UNIDADE | ESTOQUE_ATUAL | ESTOQUE_MINIMO | CATEGORIA |
|------|----------|---------|---------------|----------------|-----------|
| 001 | ACETATO DE DEXAMETASONA 1MG/G CREME | UND | 172 | 20 | Medicamentos |
| 002 | AGULHA HIPODERMICA 25 X 0,80 C/100 | UND | 53 | 10 | Descartaveis |

---

*Documento criado como parte da Issue #04*