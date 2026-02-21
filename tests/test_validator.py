import pytest
import pandas as pd
import numpy as np

from src.validator import luhn_check, limpar_dados, validar_cartoes, processar


@pytest.fixture
def df_limpo_base() -> pd.DataFrame:

    return pd.DataFrame({
        "id_transacao":   ["TXN-0001", "TXN-0002", "TXN-0003"],
        "data":           pd.to_datetime(["2026-01-10", "2026-01-11", "2026-01-12"]),
        "numero_cartao":  [
            "4532015112830366",  # Visa — válido
            "5425233430109903",  # Mastercard — válido
            "4532015112830361",  # Visa com último dígito errado — inválido
        ],
        "valor":          [199.90, 59.90, 149.90],
        "tipo_pagamento": ["credito", "debito", "credito"],
        "produto":        ["Tênis Running Pro", "Camiseta Básica", "Calça Jeans"],
        "quantidade":     ["1", "2", "1"],
        "status":         ["aprovada", "aprovada", "recusada"],
    })


@pytest.fixture
def df_sujo() -> pd.DataFrame:

    return pd.DataFrame({
        "id_transacao":   ["TXN-0001", "TXN-0001", "TXN-0003", "TXN-0004", "TXN-0005"],
        "data":           ["2026-01-10", "2026-01-10", "",         "2026-01-12", "2026-01-13"],
        "numero_cartao":  ["4532015112830366", "4532015112830366", "4532015112830366", "4532015112830366", "4532015112830366"],
        "valor":          ["199.90",           "199.90",           "59.90",            "",                 "R$ 1.299,90"],
        "tipo_pagamento": ["Credito",          "Credito",          "DEBITO",           "digital",          " Digital "],
        "produto":        ["Tênis", "Tênis", "Camiseta", "Mochila", "Jaqueta"],
        "quantidade":     ["1", "1", "2", "1", "1"],
        "status":         ["aprovada", "aprovada", "aprovada", "aprovada", "aprovada"],
    })


class TestLuhnCheck:
    
    #Testa a função luhn_check() com todos os casos possíveis.
    # Casos certos

    def test_visa_valido(self):
        assert luhn_check("4532015112830366") is True

    def test_mastercard_valido(self):
        assert luhn_check("5425233430109903") is True

    def test_elo_valido(self):
        assert luhn_check("6362970000457013") is True

    def test_cartao_com_espacos(self):
        assert luhn_check("4532 0151 1283 0366") is True

    def test_cartao_com_hifens(self):
        assert luhn_check("4532-0151-1283-0366") is True

    #Casos Errados

    def test_ultimo_digito_errado(self):
        assert luhn_check("4532015112830361") is False

    def test_mastercard_digito_errado(self):
        assert luhn_check("5425233430109907") is False

    def test_elo_digito_errado(self):
        assert luhn_check("6362970000457019") is False

    def test_numero_com_letras(self):
        assert luhn_check("4532ABC112830366") is False

    def test_numero_vazio(self):
        assert luhn_check("") is False

    def test_numero_muito_curto(self):
        assert luhn_check("123456789012") is False

    def test_numero_muito_longo(self):
        assert luhn_check("12345678901234567890") is False

    def test_apenas_zeros(self):
        # matematicamente passa no luhn, este caso será validado em uma camada separada, que valida prefixos e bandeiras
        assert luhn_check("0000000000000000") is True

    def test_retorna_bool(self):
        resultado = luhn_check("4532015112830366")
        assert isinstance(resultado, bool)

class TestLimparDados:

    def test_remove_duplicatas(self, df_sujo):
        resultado = limpar_dados(df_sujo)
        ids = resultado["id_transacao"].tolist()
        assert ids.count("TXN-0001") == 1

    def test_remove_linha_sem_data(self, df_sujo):
        resultado = limpar_dados(df_sujo)
        assert "TXN-0003" not in resultado["id_transacao"].values

    def test_remove_linha_sem_valor(self, df_sujo):
        resultado = limpar_dados(df_sujo)
        assert "TXN-0004" not in resultado["id_transacao"].values

    def test_converte_valor_para_float(self, df_sujo):
        resultado = limpar_dados(df_sujo)
        assert resultado["valor"].dtype == float

    def test_converte_valor(self, df_sujo):
        resultado = limpar_dados(df_sujo)
        linha = resultado[resultado["id_transacao"] == "TXN-0005"]
        assert not linha.empty
        assert abs(linha["valor"].values[0] - 1299.90) < 0.01

    def test_converte_data_para_datetime(self, df_sujo):
        resultado = limpar_dados(df_sujo)
        assert pd.api.types.is_datetime64_any_dtype(resultado["data"])

    def test_normaliza_tipo_pagamento_para_lowercase(self, df_sujo):
        resultado = limpar_dados(df_sujo)
        for valor in resultado["tipo_pagamento"]:
            assert valor == valor.lower().strip()

    def test_retorna_dataframe(self, df_sujo):
        resultado = limpar_dados(df_sujo)
        assert isinstance(resultado, pd.DataFrame)


class TestValidarCartoes:
    # Testa a função validar_cartoes() e a separação dos dois grupos.

    def test_retorna_dois_dataframes(self, df_limpo_base):
        df_validos, df_suspeitos = validar_cartoes(df_limpo_base)
        assert isinstance(df_validos, pd.DataFrame)
        assert isinstance(df_suspeitos, pd.DataFrame)

    def test_separa_validos_corretamente(self, df_limpo_base):
        df_validos, _ = validar_cartoes(df_limpo_base)
        assert len(df_validos) == 2

    def test_separa_suspeitos_corretamente(self, df_limpo_base):
        _, df_suspeitos = validar_cartoes(df_limpo_base)
        assert len(df_suspeitos) == 1

    def test_suspeitos_tem_coluna_motivo(self, df_limpo_base):
        _, df_suspeitos = validar_cartoes(df_limpo_base)
        assert "motivo_auditoria" in df_suspeitos.columns

    def test_nenhum_cartao_invalido_em_validos(self, df_limpo_base):
        df_validos, _ = validar_cartoes(df_limpo_base)
        for numero in df_validos["numero_cartao"]:
            assert luhn_check(str(numero)) is True, (
                f"Cartão inválido encontrado em df_validos: {numero}"
            )

    def test_total_preservado(self, df_limpo_base):
        df_validos, df_suspeitos = validar_cartoes(df_limpo_base)
        assert len(df_validos) + len(df_suspeitos) == len(df_limpo_base)


class TestProcessar:
   
    def test_processar_retorna_dois_dataframes(self, df_sujo):
        df_validos, df_suspeitos = processar(df_sujo)
        assert isinstance(df_validos, pd.DataFrame)
        assert isinstance(df_suspeitos, pd.DataFrame)

    def test_processar_com_csv_real(self):
        from src.loader import load_file
        df_bruto = load_file("data/exemplo_transacoes.csv")
        df_validos, df_suspeitos = processar(df_bruto)
       
        assert len(df_suspeitos) >= 5

        assert len(df_validos) > 0

        for numero in df_validos["numero_cartao"]:
            assert luhn_check(str(numero)) is True