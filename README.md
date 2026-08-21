# 📦 Inventory Management Dashboard

Aplicativo de controle de estoque em Python com Streamlit, focado em ambiente clínico/CDT. O projeto permite cadastrar produtos, controlar entradas e saídas, visualizar alertas de estoque baixo e importar planilhas em massa.

---

# 🚀 Funcionalidades

✅ Cadastro de produtos
✅ Controle de estoque por unidade e categoria
✅ Registro de entradas e saídas
✅ Alertas automáticos de estoque baixo
✅ Dashboard com indicadores de estoque
✅ Importação de planilhas CSV/XLSX
✅ Revisão e validação de dados antes da importação
✅ Persistência local em SQLite

---

# 🛠️ Stack

- Python
- Streamlit
- Pandas
- SQLite
- NumPy
- OpenPyXL

---

# 📁 Estrutura do projeto

```bash
Inventory-Management-Dashboard-using-Streamlit/
├── app.py
├── importacao_em_massa.py
├── validacao.py
├── smoke_test.py
├── TEMPLATE_IMPORTACAO_CDT.csv
├── requirements.txt
├── README.md
├── image.png
├── runtime.txt
├── .gitignore
└── legacy/
```

A versão principal de manutenção é `app.py`. Os módulos de suporte ativos são `validacao.py` e `importacao_em_massa.py`; arquivos do histórico e variantes antigas foram arquivados em `legacy/` para manter o projeto enxuto e estável.

---

# ⚙️ Instalação

## 1) Clonar o repositório

```bash
git clone https://github.com/IsraelSiq/Inventory-Management-Dashboard-using-Streamlit.git
cd Inventory-Management-Dashboard-using-Streamlit
```

## 2) Criar ambiente virtual

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3) Instalar dependências

```bash
pip install -r requirements.txt
```

---

# ▶️ Executar a aplicação

```bash
streamlit run app.py
```

# 🧪 Teste local rápido

```bash
python smoke_test.py
```

O script valida o fluxo principal de cadastro, entrada, saída e alertas do estoque usando o banco SQLite local do projeto.

---

# 📊 Fluxo principal

## Dashboard
- total de produtos
- valor em estoque
- quantidade de itens em estoque baixo

## Produtos
- cadastrar produto
- validar código e nome
- controlar categoria, unidade e estoque mínimo

## Entradas
- registrar material recebido
- atualizar saldo do produto
- gravar movimentação no histórico

## Saídas
- registrar consumo/transferência
- validar saldo disponível

## Alertas
- notificar quando o estoque estiver abaixo do mínimo

## Importação em massa
- carregar arquivo CSV/XLSX
- validar colunas e dados
- revisar itens antes de importar
- confirmar gravação no banco

---

# 🧾 Banco de dados

O sistema usa SQLite localmente. O banco é criado automaticamente no diretório do projeto. As tabelas principais são:

- `produtos`
- `movimentacoes`
- `alertas`

---

# 📸 Interface

![Dashboard](image.png)

---

# 🔒 Melhorias planejadas

- unificar uma versão oficial do aplicativo
- melhorar regras de negócio e integridade do banco
- reduzir duplicação entre versões do app
- ampliar testes automatizados
- revisar documentação e fluxo de manutenção

---

# 📄 Licença

Este projeto está em desenvolvimento e pode ser usado conforme a licença da organização/autor do repositório.
