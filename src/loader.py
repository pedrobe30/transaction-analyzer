import pandas as pd
from pathlib import Path

colunas_obrigatorias = {
    "id_transacao",
    "data",
    "numero_cartao",
    "valor",
    "tipo_pagamento",
    "produto",
    "status",
}

formatos_aceitos = {".csv", ".xlsx"}

class FormatoNaoSuportadoError(Exception):
    pass

class ColunasFaltandoError(Exception):
    def __init__(self, colunas_faltando: set):
        self.colunas_faltando = colunas_faltando
        nomes = ", ".join(sorted(colunas_faltando))
        super().__init__(
            f"Arquivo inválido. Colunas obrigatorias ausentes: {nomes}"
        )

def load_file(caminho: str) -> pd.DataFrame:
    caminho = Path(caminho)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )
    
    extensao = caminho.suffix.lower()

    if extensao == ".csv":
        df = _carregar_csv(caminho)
    elif extensao == ".xlsx":
        df = _carregar_excel(caminho)
    else:
        raise FormatoNaoSuportadoError(
            f"Formato '{extensao}' não suportado "
            f"Envie um arquivo .csv ou .xlsx"
        )
    
    _validar_colunas(df)

    return df

def _carregar_csv(caminho: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(
            caminho,
            sep=None,
            engine="python",
            dtype=str,
            keep_default_na=False
        )
        return df
    except Exception as e:
        raise ValueError(
            f"Erro ao ler o arquivo CSV: {e}. "
            f"Verifique se o arquivo não está corrompido."
        ) from e

def _carregar_excel(caminho: Path) -> pd.DataFrame:
    try:
        df = pd.read_excel(
            caminho,
            sheet_name=0,   
            dtype=str,      
            keep_default_na=False,
        )
        return df
    except Exception as e:
        raise ValueError(
            f"Erro ao ler o arquivo Excel: {e}. "
            f"Verifique se o arquivo é um .xlsx válido e não está protegido por senha."
        ) from e

def _validar_colunas(df: pd.DataFrame) -> None:
    
    colunas_do_arquivo = {col.lower().strip() for col in df.columns}

    colunas_faltando = colunas_obrigatorias - colunas_do_arquivo

    if colunas_faltando:
        raise ColunasFaltandoError(colunas_faltando)
    
    df.columns = [col.lower().strip() for col in df.columns]