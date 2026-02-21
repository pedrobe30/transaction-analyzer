import csv
import random
from datetime import datetime, timedelta

# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

random.seed(42)  # Garante que o resultado seja igual toda vez que rodar

ARQUIVO_SAIDA = "data/exemplo_transacoes.csv"

# ============================================================
# DADOS BASE PARA GERAÇÃO
# ============================================================

PRODUTOS = [
    ("Tênis Running Pro",     280.00),
    ("Camiseta Básica",        59.90),
    ("Calça Jeans Slim",      149.90),
    ("Mochila Esportiva",     189.90),
    ("Boné Aba Reta",          49.90),
    ("Meias Kit com 6",        39.90),
    ("Jaqueta Corta-Vento",   229.90),
    ("Shorts Academia",        79.90),
    ("Tênis Casual Urbano",   199.90),
    ("Cinto de Couro",         89.90),
]

TIPOS_PAGAMENTO = ["credito", "debito", "digital"]

# Números de cartão VÁLIDOS pelo Algoritmo de Luhn
# Fonte: números de teste públicos para desenvolvimento
CARTOES_VALIDOS = [
    "4532015112830366",  # Visa
    "5425233430109903",  # Mastercard
    "4916338506082832",  # Visa
    "5200828282828210",  # Mastercard
    "4539578763621486",  # Visa
    "4916338506082832",  # Visa
    "6362970000457013",  # Elo (formato real)
    "6362970000457013",  # Elo
    "4929420243600962",  # Visa
    "5105105105105100",  # Mastercard
    "4532015112830366",  # Visa
    "4556737586899855",  # Visa
    "5425233430109903",  # Mastercard
    "4716184876496380",  # Visa
    "5105105105105100",  # Mastercard
]

# Números de cartão INVÁLIDOS propositalmente (falham no Luhn)
# Criados alterando o último dígito de cartões válidos
CARTOES_INVALIDOS = [
    "4532015112830361",  # Visa com último dígito errado
    "5425233430109907",  # Mastercard com último dígito errado
    "6362970000457019",  # Elo com último dígito errado
    "4929420243600965",  # Visa com último dígito errado
    "5105105105105108",  # Mastercard com último dígito errado
]

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def gerar_datas(quantidade: int) -> list[str]:
    """
    Gera datas aleatórias distribuídas entre novembro/2025 e janeiro/2026.
    
    Usamos 3 meses diferentes para que a métrica de 'faturamento por período'
    tenha variação e mostre um gráfico com sentido.
    """
    data_inicio = datetime(2025, 11, 1)
    data_fim = datetime(2026, 1, 31)
    diferenca = (data_fim - data_inicio).days

    datas = []
    for _ in range(quantidade):
        dias_aleatorios = random.randint(0, diferenca)
        data = data_inicio + timedelta(days=dias_aleatorios)
        datas.append(data.strftime("%Y-%m-%d"))

    return datas


def gerar_id(numero: int) -> str:
    """Gera um ID único no formato TXN-0001, TXN-0002, etc."""
    return f"TXN-{numero:04d}"


def gerar_transacao(numero: int, data: str, cartao: str, eh_invalido: bool) -> dict:
    """
    Gera uma transação completa com todos os campos do CSV.
    
    Parâmetros:
        numero     : número sequencial da transação
        data       : data no formato YYYY-MM-DD
        cartao     : número do cartão (pode ser válido ou inválido)
        eh_invalido: se True, o status será 'recusada' com mais frequência
    """
    produto, preco_base = random.choice(PRODUTOS)
    quantidade = random.randint(1, 3)
    valor = round(preco_base * quantidade, 2)

    tipo_pagamento = random.choice(TIPOS_PAGAMENTO)

    # Transações com cartão inválido têm maior chance de serem recusadas
    # (simula o comportamento real de sistemas de pagamento)
    if eh_invalido:
        status = random.choice(["recusada", "recusada", "recusada", "aprovada"])
    else:
        status = random.choice(["aprovada", "aprovada", "aprovada", "recusada"])

    return {
        "id_transacao":   gerar_id(numero),
        "data":           data,
        "numero_cartao":  cartao,
        "valor":          valor,
        "tipo_pagamento": tipo_pagamento,
        "produto":        produto,
        "quantidade":     quantidade,
        "status":         status,
    }


# ============================================================
# GERAÇÃO DO CSV
# ============================================================

def gerar_dados() -> list[dict]:
    """
    Monta a lista completa de transações que vai para o CSV.
    
    Estratégia de composição:
    - 30 transações normais com cartões válidos
    - 5 transações com cartões inválidos (propositais, para testar o Luhn)
    - 3 transações com campos nulos (para testar a limpeza de dados)
    Total: 38 linhas
    """
    transacoes = []
    datas = gerar_datas(38)
    contador = 1

    # --- 30 transações normais ---
    print("Gerando 30 transações normais...")
    for i in range(30):
        cartao = random.choice(CARTOES_VALIDOS)
        transacao = gerar_transacao(contador, datas[i], cartao, eh_invalido=False)
        transacoes.append(transacao)
        contador += 1

    # --- 5 transações com cartões inválidos ---
    # Cada cartão inválido aparece exatamente uma vez
    print("Inserindo 5 transações com cartões inválidos (teste do Luhn)...")
    for i, cartao_invalido in enumerate(CARTOES_INVALIDOS):
        transacao = gerar_transacao(contador, datas[30 + i], cartao_invalido, eh_invalido=True)
        transacoes.append(transacao)
        contador += 1

    # --- 3 transações com campos nulos ---
    # Simula dados bagunçados que chegam do mundo real
    print("Inserindo 3 transações com campos nulos (teste de limpeza)...")

    # Linha sem valor (campo valor = vazio)
    transacoes.append({
        "id_transacao":   gerar_id(contador),
        "data":           datas[35],
        "numero_cartao":  random.choice(CARTOES_VALIDOS),
        "valor":          "",           # <- NULO PROPOSITAL
        "tipo_pagamento": "credito",
        "produto":        "Tênis Running Pro",
        "quantidade":     1,
        "status":         "aprovada",
    })
    contador += 1

    # Linha sem data (campo data = vazio)
    transacoes.append({
        "id_transacao":   gerar_id(contador),
        "data":           "",           # <- NULO PROPOSITAL
        "numero_cartao":  random.choice(CARTOES_VALIDOS),
        "valor":          99.90,
        "tipo_pagamento": "debito",
        "produto":        "Camiseta Básica",
        "quantidade":     1,
        "status":         "aprovada",
    })
    contador += 1

    # Linha completamente duplicada (cópia exata da primeira transação)
    duplicada = transacoes[0].copy()
    transacoes.append(duplicada)
    print("Inserindo 1 linha duplicada (teste de deduplicação)...")

    # Embaralha para que os inválidos e nulos não fiquem todos no final
    random.shuffle(transacoes)

    return transacoes


def salvar_csv(transacoes: list[dict], caminho: str) -> None:
    """Salva a lista de transações como arquivo CSV."""
    colunas = [
        "id_transacao",
        "data",
        "numero_cartao",
        "valor",
        "tipo_pagamento",
        "produto",
        "quantidade",
        "status",
    ]

    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(transacoes)


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

if __name__ == "__main__":
    import os

    # Cria a pasta data/ se não existir
    os.makedirs("data", exist_ok=True)

    print("\n=== Gerando CSV de dados fictícios ===\n")
    transacoes = gerar_dados()
    salvar_csv(transacoes, ARQUIVO_SAIDA)

    # Resumo do que foi gerado
    total = len(transacoes)
    invalidos = sum(1 for t in transacoes if t["numero_cartao"] in CARTOES_INVALIDOS)
    nulos = sum(1 for t in transacoes if t["valor"] == "" or t["data"] == "")

    print(f"\n✅ Arquivo gerado: {ARQUIVO_SAIDA}")
    print(f"   Total de linhas : {total}")
    print(f"   Cartões inválidos (Luhn): {invalidos}")
    print(f"   Linhas com campos nulos : {nulos}")
    print(f"   Linhas duplicadas       : 1")
    print("\nPróximo passo: rode o loader.py para carregar e validar este arquivo.")