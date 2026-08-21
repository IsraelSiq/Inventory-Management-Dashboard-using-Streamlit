# Inventory Management Dashboard

Aplicativo de controle de estoque em Python com Streamlit, focado em operação clínica e almoxarifado. O projeto centraliza cadastro de produtos, movimentação de estoque, alertas, importação em massa e exportação de relatórios.

Status atual: versão principal validada e estável, com foco em manutenção da aplicação ativa e no reforço de validações de negócio.

---

## O que foi entregue

- validação de cadastro de produtos e regras de estoque
- prevenção de código duplicado e movimentações inválidas
- integridade do banco SQLite com chaves estrangeiras
- importação em massa com checagem de colunas, valores e duplicidades
- suporte a PDF textual e fallback OCR para PDFs digitalizados
- geração de relatório do estoque com valor total e exportação para Excel
- testes automatizados focados em regressão

---

## Aplicação principal

A execução principal do projeto fica em:

- `app.py` — dashboard principal, cadastro, movimentações, alertas e relatórios

Módulos ativos de apoio:

- `validacao.py` — padronização e validação de dados
- `importacao.py` — leitura/importação de arquivos e processamento de PDFs
- `importacao_em_massa.py` — fluxo de importação em massa e relatório de importação

Arquivos históricos/variantes antigas continuam existindo no repositório, mas não são a fonte de verdade do fluxo ativo. A manutenção do projeto deve priorizar `app.py` e os módulos de suporte diretamente utilizados por ela.

---

## Estrutura do repositório

```bash
Inventory-Management-Dashboard-using-Streamlit/
├── app.py
├── importacao.py
├── importacao_em_massa.py
├── validacao.py
├── smoke_test.py
├── requirements.txt
├── README.md
├── TEMPLATE_IMPORTACAO_CDT.csv
├── image.png
├── tests/
│   ├── test_pdf_textual.py
│   ├── test_pdf_ocr.py
│   ├── test_pdf_formatos_cdt.py
│   └── test_relatorios.py
├── docs/
├── app/
├── app_com_importacao.py
├── app_com_revisao.py
├── app_final_v2.py
├── normalizar_planilha_cdt.py
├── revisao.py
├── tema.py
└── .gitignore
```

---

## Stack

- Python
- Streamlit
- SQLite
- Pandas
- NumPy
- OpenPyXL
- pdfplumber
- pdf2image
- pytesseract
- pytest

---

## Instalação local

### 1) Clonar o repositório

```bash
git clone https://github.com/IsraelSiq/Inventory-Management-Dashboard-using-Streamlit.git
cd Inventory-Management-Dashboard-using-Streamlit
```

### 2) Criar ambiente virtual

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Instalar dependências

```bash
pip install -r requirements.txt
```

Se houver uso de OCR em PDFs, confirme também que o executável do Tesseract está instalado no sistema operacional.

---

## Como executar

```bash
streamlit run app.py
```

A interface principal permite:

- Dashboard com resumo geral
- Cadastro de produtos
- Registro de entradas e saídas
- Alertas de estoque baixo
- Relatórios e exportação em Excel
- Importação em massa

---

## Testes locais

### Smoke test do fluxo principal

```bash
python smoke_test.py
```

### Suite de testes automatizados

```bash
pytest -q
```

Cobertura atual:

- fluxo principal do inventário
- extração textual de PDFs
- OCR para PDFs digitalizados
- classificação de formatos CDT
- geração e exportação de relatórios

---

## Regras de negócio reforçadas

- código de produto obrigatório e único
- nome do produto obrigatório
- valores negativos são rejeitados
- quantidade de movimentação deve ser positiva
- saída só é permitida quando existe saldo suficiente
- banco SQLite reforça integridade referencial entre produtos, movimentações e alertas

## Perfil de acesso

A aplicação agora também expõe perfis de acesso por papel:

- `Administrador`: acesso completo ao cadastro, movimentação, alertas e relatórios
- `Operador`: acesso às movimentações e alertas, sem cadastro de produtos
- `Visualização`: somente dashboard e relatórios

Isso ajuda a controlar o uso da interface em ambientes compartilhados sem impactar o fluxo principal de operação.

## Controle de lote e validade

Produtos marcados com `Controla lote` exigem lote e validade obrigatórios ao cadastrar e em cada movimentação de entrada/saída. O formato da validade é validado como `YYYY-MM-DD`.

Isso reduz riscos operacionais em itens sensíveis, reduzindo cadastros incompletos e movimentações sem rastreabilidade.

---

## Banco de dados

O sistema usa SQLite local em disco. O banco é criado automaticamente quando a aplicação inicia.

Tabelas principais:

- `produtos`
- `movimentacoes`
- `alertas`

---

## Status do projeto

O projeto está em estado validado para uso local e manutenção incremental. Os itens críticos de validação do fluxo principal foram corrigidos e cobertos por testes de regressão.

Próximas melhorias, quando desejadas, devem seguir a ordem de prioridade do backlog e sem abrir escopo de refatoração ampla em arquivos de execução principal.

---

## Licença

Este repositório é mantido para fins de desenvolvimento e uso interno/institucional conforme a política do projeto e do autor responsável.
