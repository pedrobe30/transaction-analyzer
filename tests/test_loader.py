import pytest
import pandas as pd
import tempfile
import os
from src.loader import load_file, FormatoNaoSuportadoError, ColunasFaltandoError


@pytest.fixture
def dados_validos() -> dict:
    return {
        "id_transacao":   ["TXN-0001", "TXN-0002"],
        "data":           ["2026-01-10", "2026-01-11"],
        "numero_cartao":  ["4532015112830366", "5425233430109903"],
        "valor":          ["199.90", "59.90"],
        "tipo_pagamento": ["credito", "debito"],
        "produto":        ["Tênis Running Pro", "Camiseta Básica"],
        "quantidade":     ["1", "2"],
        "status":         ["aprovada", "aprovada"],
    }

@pytest.fixture
def csv_valido(dados_validos, tmp_path) -> str:
    df = pd.DataFrame(dados_validos)
    caminho = tmp_path / "transacoes_teste.csv"
    df.to_csv(caminho, index=False)
    return str(caminho)

@pytest.fixture
def excel_valido(dados_validos, tmp_path) -> str:
    df = pd.DataFrame(dados_validos)
    caminho = tmp_path / "transacoes_teste.xlsx"
    df.to_excel(caminho, index=False)
    return str(caminho)


@pytest.fixture
def csv_sem_coluna(tmp_path) -> str:
    dados_incompletos = {
        "id_transacao":   ["TXN-0001"],
        "data":           ["2026-01-10"],
        "numero_cartao":  ["4532015112830366"],
        # 'valor' 
        "tipo_pagamento": ["credito"],
        "produto":        ["Tênis Running Pro"],
        "status":         ["aprovada"],
    }
    df = pd.DataFrame(dados_incompletos)
    caminho = tmp_path / "sem_coluna.csv"
    df.to_csv(caminho, index=False)
    return str(caminho)

class TestCarregarCSV:
    def test_csv_valido_retorna_dataframe(self, csv_valido):
        resultado = load_file(csv_valido)
        assert isinstance(resultado, pd.DataFrame)

    def test_csv_valido_tem_linhas(self, csv_valido):
        resultado = load_file(csv_valido)
        assert len(resultado) == 2

    def test_csv_valido_tem_colunas_corretas(self, csv_valido):
        resultado = load_file(csv_valido)
        for coluna in resultado.columns:
            assert coluna == coluna.lower(), f"Coluna '{coluna}' deveria estar em lowercase"

    def test_csv_com_ponto_virgula(self, dados_validos, tmp_path):
        df = pd.DataFrame(dados_validos)
        caminho = tmp_path / "br_separador.csv"
        df.to_csv(caminho, index=False, sep=";")  

        resultado = load_file(str(caminho))
        assert isinstance(resultado, pd.DataFrame)
        assert len(resultado.columns) > 1 

class TestCarregarExcel:
    def test_excel_valido_retorna_dataframe(self, excel_valido):
        resultado = load_file(excel_valido)
        assert isinstance(resultado, pd.DataFrame)

    def test_excel_valido_tem_linhas(self, excel_valido):
        resultado = load_file(excel_valido)
        assert len(resultado) == 2


class TestErros:
    def test_arquivo_inexistente_lanca_erro(self):

        with pytest.raises(FileNotFoundError):
            load_file("caminho/que/nao/existe.csv")

    def test_formato_invalido_lanca_erro(self, tmp_path):
        arquivo_txt = tmp_path / "dados.txt"
        arquivo_txt.write_text("id,valor\n001,100")

        with pytest.raises(FormatoNaoSuportadoError):
            load_file(str(arquivo_txt))

    def test_formato_pdf_lanca_erro(self, tmp_path):
        arquivo_pdf = tmp_path / "relatorio.pdf"
        arquivo_pdf.write_bytes(b"%PDF-1.4 fake content")

        with pytest.raises(FormatoNaoSuportadoError):
            load_file(str(arquivo_pdf))

    def test_coluna_faltando_lanca_erro(self, csv_sem_coluna):

        with pytest.raises(ColunasFaltandoError):
            load_file(csv_sem_coluna)

    def test_erro_informa_quais_colunas_faltam(self, csv_sem_coluna):
       
        with pytest.raises(ColunasFaltandoError) as info_erro:
            load_file(csv_sem_coluna)

        # info_erro.value acessa o objeto da exceção
        assert "valor" in info_erro.value.colunas_faltando

    def test_colunas_uppercase_sao_aceitas(self, dados_validos, tmp_path):

        dados_uppercase = {k.upper(): v for k, v in dados_validos.items()}
        df = pd.DataFrame(dados_uppercase)
        caminho = tmp_path / "uppercase.csv"
        df.to_csv(caminho, index=False)

        resultado = load_file(str(caminho))
        assert isinstance(resultado, pd.DataFrame)
        assert "valor" in resultado.columns  # lowercase
