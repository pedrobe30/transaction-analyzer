BANDEIRAS = [
    {
        "nome":         "Elo",
        "prefixos":     [
            "636368", "636297", "504175", "438935", "451416",
            "509048", "509067", "509049", "509069", "509050",
            "509074", "509068", "509040", "509045", "509051",
            "509046", "509066", "509042", "509064", "509047",
            "627780", "636369", "650031", "650032", "650033",
            "650035", "650036", "650037", "650038", "650039",
            "6362", "6516", "6550", "4011", "4576",
        ],
        "comprimentos": {16},
        "cor":          "#003399",
        "texto_cor":    "#FFFFFF",
        "emoji":        "🔵",
    },
    {
        "nome":         "American Express",
        "prefixos":     ["34", "37"],
        "comprimentos": {15},
        "cor":          "#007BC1",
        "texto_cor":    "#FFFFFF",
        "emoji":        "🟦",
    },
    {
        "nome":         "Hipercard",
        "prefixos":     ["606282", "3841"],
        "comprimentos": {13, 16, 19},
        "cor":          "#822124",
        "texto_cor":    "#FFFFFF",
        "emoji":        "🔴",
    },
    {
        "nome":         "Maestro",
        "prefixos":     ["6304", "6759", "6761", "6762", "6763"],
        "comprimentos": {12, 13, 14, 15, 16, 17, 18, 19},
        "cor":          "#CC0000",
        "texto_cor":    "#FFFFFF",
        "emoji":        "🔴",
    },
    {
        "nome":         "Mastercard",
        "prefixos":     ["51", "52", "53", "54", "55"],
        "comprimentos": {16},
        "cor":          "#252525",
        "texto_cor":    "#FFFFFF",
        "emoji":        "🟠",
        "range":        (2221, 2720),
    },
    {
        "nome":         "Visa",
        "prefixos":     ["4"],
        "comprimentos": {13, 16, 19},
        "cor":          "#1A1F71",
        "texto_cor":    "#FFFFFF",
        "emoji":        "🔷",
    },
]

BANDEIRA_DESCONHECIDA = {
    "nome":      "Desconhecida",
    "cor":       "#6B7280",
    "texto_cor": "#FFFFFF",
    "emoji":     "❓",
}


def detectar_bandeira(numero: str) -> dict:
    numero = numero.replace(" ", "").replace("-", "").strip()

    if not numero.isdigit() or len(numero) < 13:
        return BANDEIRA_DESCONHECIDA

    comprimento = len(numero)

    for bandeira in BANDEIRAS:
        if comprimento not in bandeira["comprimentos"]:
            continue

        prefixos_ordenados = sorted(bandeira["prefixos"], key=len, reverse=True)

        for prefixo in prefixos_ordenados:
            if numero.startswith(prefixo):
                return bandeira

        if "range" in bandeira:
            inicio, fim = bandeira["range"]
            if len(numero) >= 4 and inicio <= int(numero[:4]) <= fim:
                return bandeira

    return BANDEIRA_DESCONHECIDA


def mascarar_numero(numero: str) -> str:
    numero_limpo = numero.replace(" ", "").replace("-", "").strip()

    if not numero_limpo.isdigit() or len(numero_limpo) < 13:
        return numero

    inicio = numero_limpo[:6]
    fim    = numero_limpo[-4:]
    meio   = "*" * (len(numero_limpo) - 10)

    return f"{inicio} {meio} {fim}"


def badge_html(bandeira: dict) -> str:
    return (
        f'<span style="'
        f'background-color:{bandeira["cor"]};'
        f'color:{bandeira["texto_cor"]};'
        f'padding:2px 10px;'
        f'border-radius:12px;'
        f'font-size:0.78rem;'
        f'font-weight:600;'
        f'white-space:nowrap;'
        f'">'
        f'{bandeira["emoji"]} {bandeira["nome"]}'
        f'</span>'
    )


def enriquecer_dataframe(df):
    df = df.copy()

    info = df["numero_cartao"].astype(str).apply(detectar_bandeira)

    df["bandeira"]         = info.apply(lambda b: b["nome"])
    df["bandeira_emoji"]   = info.apply(lambda b: b["emoji"])
    df["cartao_mascarado"] = df["numero_cartao"].astype(str).apply(mascarar_numero)

    return df