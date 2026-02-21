import pandas as pd
from pathlib import Path
import io


COLUNAS_OBRIGATORIAS = {
    "id_transacao", "data", "numero_cartao",
    "valor", "tipo_pagamento", "produto", "status",
}


class FormatoNaoSuportadoError(Exception):
    pass


class ColunasFaltandoError(Exception):
    def __init__(self, colunas_faltando: set):
        self.colunas_faltando = colunas_faltando
        nomes = ", ".join(sorted(colunas_faltando))
        super().__init__(f"Arquivo inválido. Colunas obrigatórias ausentes: {nomes}")


def load_file(arquivo) -> pd.DataFrame:
    if isinstance(arquivo, (str, Path)):
        return _carregar_de_disco(Path(arquivo))
    else:
        return _carregar_de_objeto(arquivo)


def _carregar_de_disco(caminho: Path) -> pd.DataFrame:
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: '{caminho}'.")

    extensao = caminho.suffix.lower()

    if extensao == ".csv":
        df = pd.read_csv(caminho, sep=None, engine="python", dtype=str, keep_default_na=False)
    elif extensao == ".xlsx":
        df = pd.read_excel(caminho, sheet_name=0, dtype=str, keep_default_na=False)
    else:
        raise FormatoNaoSuportadoError(f"Formato '{extensao}' não suportado. Use .csv ou .xlsx.")

    _validar_colunas(df)
    return df


def _carregar_de_objeto(arquivo_obj) -> pd.DataFrame:
    nome = getattr(arquivo_obj, "name", "")
    extensao = Path(nome).suffix.lower()

    if extensao == ".csv":
        conteudo = arquivo_obj.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(conteudo), sep=None, engine="python",
                         dtype=str, keep_default_na=False)
    elif extensao == ".xlsx":
        df = pd.read_excel(arquivo_obj, sheet_name=0, dtype=str, keep_default_na=False)
    else:
        raise FormatoNaoSuportadoError(f"Formato '{extensao}' não suportado. Use .csv ou .xlsx.")

    _validar_colunas(df)
    return df


def _validar_colunas(df: pd.DataFrame) -> None:
    colunas_do_arquivo = {col.lower().strip() for col in df.columns}
    colunas_faltando = COLUNAS_OBRIGATORIAS - colunas_do_arquivo
    if colunas_faltando:
        raise ColunasFaltandoError(colunas_faltando)
    df.columns = [col.lower().strip() for col in df.columns]