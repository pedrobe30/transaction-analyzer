# transaction-analyzer
Sistema de análise de transações com validação de cartões (Algoritmo de Luhn) e geração automática de relatórios em Excel.

# 💳 Transaction Analyzer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)
![openpyxl](https://img.shields.io/badge/openpyxl-3.1+-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-8.0+-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![CI](https://img.shields.io/github/actions/workflow/status/pedrobe30/transaction-analyzer/ci.yml?style=for-the-badge&label=CI&logo=githubactions&logoColor=white)

**Sistema de análise de transações financeiras com validação de cartões com Algoritmo de Luhn,
detecção automática de bandeiras e geração de relatórios Excel profissionais.**

[🚀 Acessar o sistema](#deploy) · [📖 Como usar](#como-usar) · [🧪 Testes](#testes) · [📁 Estrutura](#estrutura)

</div>

---

## 🎯 Sobre o projeto

Pequenas e médias empresas geram diariamente dados de transações financeiras em planilhas manuais ou exportações de ERPs — dados bagunçados, com erros e sem nenhuma análise. O **Transaction Analyzer** resolve isso:

1. Recebe um arquivo CSV ou Excel com transações brutas
2. **Valida cada número de cartão** com o Algoritmo de Luhn
3. **Detecta a bandeira** de cada cartão (Visa, Mastercard, Elo, Amex...)
4. Limpa os dados: remove duplicados, nulos e inconsistências
5. Calcula métricas de negócio em tempo real
6. Gera automaticamente um **relatório Excel profissional** com 5 abas

O projeto foi desenvolvido como portfólio técnico, simulando parte do pipeline de validação e análise que sistemas reais de meios de pagamento executam

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 🔍 **Validação Luhn** | Verifica matematicamente cada número de cartão antes de processar |
| 🏷️ **Detector de bandeiras** | Identifica Visa, Mastercard, Elo, Amex, Maestro e Hipercard por prefixo |
| 🧹 **Limpeza de dados** | Remove duplicados, trata nulos e normaliza tipos automaticamente |
| 📊 **Métricas de negócio** | Faturamento, ticket médio, taxa de aprovação, top produtos e breakdown por pagamento |
| 📥 **Relatório Excel** | 5 abas formatadas: Resumo Executivo, Por Período, Top Produtos, Verificadas e Auditoria |
| ⚠️ **Aba de Auditoria** | Transações suspeitas separadas com motivo documentado |
| 🖥️ **Interface web** | Upload e download via Streamlit, sem instalar nada extra |
| 🧪 **Testes automatizados** | 30+ testes com pytest cobrindo Luhn, métricas e carregamento |
| 🔄 **CI/CD** | GitHub Actions roda os testes a cada push automaticamente |

---

## 🧮 O Algoritmo de Luhn

O Luhn é o algoritmo usado por **todas as bandeiras de cartão do mundo** para validar números. Criado em 1954 por Hans Peter Luhn (IBM), detecta qualquer erro de digitação em um único dígito.

**Como funciona em 4 passos:**

```
Número: 4 5 3 2 0 1 5 1 1 2 8 3 0 3 6 6
                                        ↑ dígito verificador

1. Inverte o número
2. Dobra os dígitos nas posições pares (2ª, 4ª, 6ª...)
3. Se o dobro > 9, subtrai 9
4. Soma tudo — se divisível por 10, o cartão é válido ✅
```

**Implementação no projeto:**

```python
def luhn_check(numero: str) -> bool:
    numero = numero.replace(" ", "").replace("-", "")
    if not numero.isdigit() or not (13 <= len(numero) <= 19):
        return False

    digitos = [int(d) for d in numero[::-1]]
    soma = 0
    for posicao, digito in enumerate(digitos):
        if posicao % 2 == 1:
            dobrado = digito * 2
            soma += dobrado - 9 if dobrado > 9 else dobrado
        else:
            soma += digito

    return soma % 10 == 0
```

---

## 🏷️ Detecção de Bandeiras

A detecção é feita por **prefixo numérico (BIN — Bank Identification Number)**:

| Bandeira | Prefixos | Comprimento |
|---|---|---|
| 🔷 Visa | Começa com `4` | 13, 16 ou 19 dígitos |
| 🟠 Mastercard | `51`–`55` ou range `2221`–`2720` | 16 dígitos |
| 🔵 Elo | `636368`, `636297`, `6362`, `6516`, `4011`... | 16 dígitos |
| 🟦 American Express | `34` ou `37` | 15 dígitos |
| 🔴 Maestro | `6304`, `6759`, `6761`... | 12–19 dígitos |
| 🔴 Hipercard | `606282` ou `3841` | 13, 16 ou 19 dígitos |

## 🚀 Como usar

### Pré-requisitos

- Python 3.10+
- pip

### Instalação

```bash
# Clone o repositório
git clone https://github.com/pedrobe30/transaction-analyzer.git
cd transaction-analyzer

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# Instale as dependências
pip install -r requirements.txt
```

### Gerar os arquivos de dados de exemplo

```bash
# Tabela 1: loja de roupas (nov/2025 – jan/2026)
python data/gerar_csv.py

# Tabela 2: TechStore Brasil — eletrônicos (mar/2026 – mai/2026)
python data/gerar_csv_eletronicos.py
```

### Rodar a interface

```bash
streamlit run src/app.py
```

Acesse `http://localhost:8501` no browser. Faça upload de um dos CSVs gerados e clique em **Analisar Transações**.

---

## 📁 Estrutura do projeto

```
transaction-analyzer/
│
├── src/                        # Código principal
│   ├── loader.py               # Leitura e validação de arquivos CSV/Excel
│   ├── validator.py            # Algoritmo de Luhn + limpeza de dados
│   ├── brand_detector.py       # Detecção de bandeira por prefixo BIN
│   ├── metrics.py              # Cálculo de KPIs de negócio
│   ├── reporter.py             # Geração do relatório Excel com openpyxl
│   └── app.py                  # Interface web com Streamlit
│
├── tests/                      # Testes automatizados
│   ├── conftest.py             # Configuração do pytest
│   ├── test_loader.py          # Testes de carregamento de arquivo
│   ├── test_validator.py       # Testes do Algoritmo de Luhn e limpeza
│   └── test_metrics.py         # Testes de cálculo de métricas
│
├── data/                       # Dados de exemplo
│   ├── gerar_csv.py            # Script: loja de roupas
│   ├── exemplo_transacoes.csv  # Dados gerados: loja de roupas
│   ├── gerar_csv_eletronicos.py# Script: TechStore Brasil
│   └── eletronicos_transacoes.csv # Dados gerados: eletrônicos
│
├── docs/
│   └── fluxogramas/            # Diagramas Mermaid do sistema
│
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions — CI automático
│
├── requirements.txt
└── README.md
```

---

## 🔄 Pipeline de dados

```
arquivo CSV/Excel
      ↓
  loader.py       → valida formato e colunas obrigatórias
      ↓
 validator.py     → Luhn · limpeza · separa válidos e suspeitos
      ↓
brand_detector.py → identifica bandeira de cada cartão válido
      ↓
  metrics.py      → faturamento · ticket médio · taxa de aprovação · top produtos
      ↓
  reporter.py     → gera Excel com 5 abas formatadas
      ↓
   app.py         → exibe KPIs + disponibiliza download
```

---

## 🧪 Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Rodar módulo específico
pytest tests/test_validator.py -v

# Ver cobertura resumida
pytest tests/ -v --tb=short
```

**Cobertura atual:** 30+ testes cobrindo:
- Algoritmo de Luhn (válidos, inválidos, edge cases)
- Carregamento de CSV e Excel (formatos, colunas, erros)
- Limpeza de dados (nulos, duplicados, tipos, formatos BR)
- Cálculo de métricas (faturamento, ticket médio, taxa, top produtos)
- Integração do pipeline completo

O **GitHub Actions** roda todos os testes automaticamente a cada `push` — o badge no topo mostra o status atual.

---

## 📊 Relatório Excel — 5 abas

| Aba | Conteúdo |
|---|---|
| 📊 Resumo Executivo | KPIs principais em cards visuais com formatação azul Elo |
| 📅 Por Período | Faturamento mensal + gráfico de barras |
| 🏆 Top Produtos | Ranking dos produtos com maior receita |
| ✅ Transações Verificadas | Lista com bandeira, número mascarado e dados completos |
| ⚠️ Auditoria | Transações com cartão inválido separadas com motivo documentado |

---

## 🛠️ Stack tecnológica

| Tecnologia | Função |
|---|---|
| **Python 3.10+** | Linguagem principal |
| **Pandas** | Leitura, limpeza e manipulação de DataFrames |
| **openpyxl** | Geração do Excel com formatação, fórmulas e gráficos |
| **Streamlit** | Interface web interativa sem HTML/CSS |
| **pytest** | Testes automatizados |
| **GitHub Actions** | CI/CD — execução automática dos testes |

---

## 👨‍💻 Autor

**Pedro Bernardo**
Técnico em Desenvolvimento de Sistemas

[![GitHub](https://img.shields.io/badge/GitHub-pedrobe30-181717?style=flat&logo=github)](https://github.com/pedrobe30)

---

<div align="center">
  <sub>Projeto desenvolvido como portfólio técnico — 2026</sub>
</div>