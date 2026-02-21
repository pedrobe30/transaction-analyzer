import pandas as pd

def luhn_check(numero: str) -> bool:

    
   
    numero = numero.replace(" ", "").replace("-", "").strip()
   
    if not numero.isdigit():
        return False

    if not (13 <= len(numero) <= 19):
        return False

    digitos = [int(d) for d in numero[::-1]]
    soma = 0

    for posicao, digito in enumerate(digitos):
      
        if posicao % 2 == 1:
            dobrado = digito * 2
            
            if dobrado > 9:
                dobrado -= 9
            soma += dobrado
        else:
            # Posições pares, apenas soma o dígito
            soma += digito

    return soma % 10 == 0



def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    
    df = df.copy()

    total_inicial = len(df)

    df = df.drop_duplicates(keep="first")
    removidas_duplicadas = total_inicial - len(df)

    df["valor"] = df["valor"].replace("", float("nan"))
    df["data"] = df["data"].replace("", float("nan"))
    df["numero_cartao"] = df["numero_cartao"].replace("", float("nan"))

    antes_nulos = len(df)
    df = df.dropna(subset=["valor", "data", "numero_cartao"])
    removidas_nulos = antes_nulos - len(df)

    df["valor"] = (
        df["valor"]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)   
        .str.replace(",", ".", regex=False)  
        .str.strip()
    )

    # Converte para número — linhas que não puderem ser convertidas viram NaN
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    # Remove linhas onde valor não pôde ser convertido
    df = df.dropna(subset=["valor"])

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data"])

    df["tipo_pagamento"] = df["tipo_pagamento"].str.lower().str.strip()

    
    total_final = len(df)
    print(f"[validator] Limpeza concluída:")
    print(f"  Linhas iniciais  : {total_inicial}")
    print(f"  Duplicadas removidas: {removidas_duplicadas}")
    print(f"  Nulos removidos  : {removidas_nulos}")
    print(f"  Linhas restantes : {total_final}")

    return df


def validar_cartoes(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:

    df = df.copy()

    df["cartao_valido"] = df["numero_cartao"].astype(str).apply(luhn_check)

    df_validos = df[df["cartao_valido"] == True].copy()
    df_suspeitos = df[df["cartao_valido"] == False].copy()

    df_suspeitos["motivo_auditoria"] = "Número de cartão inválido"

    df_validos = df_validos.drop(columns=["cartao_valido"])
    df_suspeitos = df_suspeitos.drop(columns=["cartao_valido"])

    print(f"[validator] Validação de cartões:")
    print(f"  Transações válidas  : {len(df_validos)}")
    print(f"  Transações suspeitas: {len(df_suspeitos)}")

    return df_validos, df_suspeitos


def processar(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:

    df_limpo = limpar_dados(df)
    df_validos, df_suspeitos = validar_cartoes(df_limpo)
    return df_validos, df_suspeitos