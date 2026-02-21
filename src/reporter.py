import io
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.utils import get_column_letter


COR_AZUL   = "003399"  # azul principal — cabeçalhos
COR_AZUL_CLARO = "D6E4FF"  # azul suave — linhas alternadas
COR_AMARELO    = "FFF3CD"  # amarelo suave — destaques de KPI
COR_VERDE      = "D4EDDA"  # verde — valores positivos
COR_VERMELHO   = "F8D7DA"  # vermelho suave — auditoria / alertas
COR_CINZA      = "F5F5F5"  # cinza claro — linhas alternadas
COR_BRANCO     = "FFFFFF"


def _fonte_cabecalho(tamanho: int = 11) -> Font:
    return Font(name="Arial", bold=True, color="FFFFFF", size=tamanho)

def _fonte_normal(tamanho: int = 10, negrito: bool = False) -> Font:
    return Font(name="Arial", size=tamanho, bold=negrito)

def _fundo(cor: str) -> PatternFill:
    return PatternFill("solid", start_color=cor, fgColor=cor)

def _borda_fina() -> Border:
    lado = Side(style="thin", color="CCCCCC")
    return Border(left=lado, right=lado, top=lado, bottom=lado)

def _centralizado() -> Alignment:
    return Alignment(horizontal="center", vertical="center", wrap_text=True)

def _esquerda() -> Alignment:
    return Alignment(horizontal="left", vertical="center")


def _cabecalho_aba(ws, titulo: str, subtitulo: str) -> None:
    """Escreve o cabeçalho padrão no topo de cada aba."""
    ws.merge_cells("A1:H1")
    ws["A1"] = titulo
    ws["A1"].font = Font(name="Arial", bold=True, size=16, color="FFFFFF")
    ws["A1"].fill = _fundo(COR_AZUL)
    ws["A1"].alignment = _centralizado()
    ws.row_dimensions[1].height = 35

    ws.merge_cells("A2:H2")
    ws["A2"] = subtitulo
    ws["A2"].font = Font(name="Arial", size=10, color="555555", italic=True)
    ws["A2"].alignment = _centralizado()
    ws.row_dimensions[2].height = 20


def _linha_cabecalho_tabela(ws, linha: int, colunas: list[str]) -> None:
    for col_idx, texto in enumerate(colunas, start=1):
        cel = ws.cell(row=linha, column=col_idx, value=texto)
        cel.font = _fonte_cabecalho()
        cel.fill = _fundo(COR_AZUL)
        cel.alignment = _centralizado()
        cel.border = _borda_fina()


def _linha_dados(ws, linha: int, valores: list, alternada: bool = False) -> None:
    cor = COR_CINZA if alternada else COR_BRANCO
    for col_idx, valor in enumerate(valores, start=1):
        cel = ws.cell(row=linha, column=col_idx, value=valor)
        cel.font = _fonte_normal()
        cel.fill = _fundo(cor)
        cel.border = _borda_fina()
        cel.alignment = _esquerda()


def _ajustar_colunas(ws, larguras: list[int]) -> None:
    for i, largura in enumerate(larguras, start=1):
        ws.column_dimensions[get_column_letter(i)].width = largura


def _aba_resumo(wb: Workbook, metricas: dict) -> None:

    ws = wb.active
    ws.title = "Resumo Executivo"

    _cabecalho_aba(
        ws,
        "Resumo Executivo — Transaction Analyzer",
        "Análise de transações com validação de cartões pelo Algoritmo de Luhn"
    )

    kpis = [
        ("Faturamento Total",    f"R$ {metricas['faturamento_total']:,.2f}",    COR_VERDE),
        ("Ticket Médio",         f"R$ {metricas['ticket_medio']:,.2f}",         COR_AMARELO),
        ("Taxa de Aprovação",    f"{metricas['taxa_aprovacao']}%",              COR_VERDE),
        ("Total de Transações",  str(metricas['total_transacoes']),             COR_AZUL_CLARO),
        ("Aprovadas",            str(metricas['total_aprovadas']),              COR_VERDE),
        ("Recusadas",            str(metricas['total_recusadas']),              COR_VERMELHO),
    ]

    
    linha_atual = 4
    for i, (rotulo, valor, cor) in enumerate(kpis):
        col_inicio = (i % 3) * 2 + 1  # colunas 1, 3, 5
        col_fim    = col_inicio + 1

     
        if i > 0 and i % 3 == 0:
            linha_atual += 4

        ws.merge_cells(
            start_row=linha_atual, start_column=col_inicio,
            end_row=linha_atual,   end_column=col_fim
        )
        cel_rotulo = ws.cell(row=linha_atual, column=col_inicio, value=rotulo)
        cel_rotulo.font = Font(name="Arial", bold=True, size=10, color="333333")
        cel_rotulo.fill = _fundo(COR_AZUL_CLARO)
        cel_rotulo.alignment = _centralizado()
        cel_rotulo.border = _borda_fina()
        ws.row_dimensions[linha_atual].height = 22

     
        ws.merge_cells(
            start_row=linha_atual + 1, start_column=col_inicio,
            end_row=linha_atual + 1,   end_column=col_fim
        )
        cel_valor = ws.cell(row=linha_atual + 1, column=col_inicio, value=valor)
        cel_valor.font = Font(name="Arial", bold=True, size=14, color="003399")
        cel_valor.fill = _fundo(cor)
        cel_valor.alignment = _centralizado()
        cel_valor.border = _borda_fina()
        ws.row_dimensions[linha_atual + 1].height = 30

    
    _ajustar_colunas(ws, [22, 22, 22, 22, 22, 22])


def _aba_periodo(wb: Workbook, metricas: dict) -> None:

    ws = wb.create_sheet("Por Período")
    df = metricas["faturamento_por_periodo"]

    _cabecalho_aba(ws, "Faturamento por Período", "Receita mensal de transações aprovadas")

    # --- Tabela ---
    _linha_cabecalho_tabela(ws, 4, ["Período", "Faturamento (R$)"])

    for i, row in df.iterrows():
        linha = 5 + list(df.index).index(i)
        _linha_dados(ws, linha, [str(row["periodo"]), row["faturamento"]], alternada=linha % 2 == 0)
        
        ws.cell(row=linha, column=2).number_format = 'R$ #,##0.00'


    ultima_linha_dados = 4 + len(df)
    linha_total = ultima_linha_dados + 1
    ws.cell(row=linha_total, column=1, value="TOTAL").font = _fonte_normal(negrito=True)
    ws.cell(row=linha_total, column=1).fill = _fundo(COR_AZUL)
    ws.cell(row=linha_total, column=1).font = _fonte_cabecalho()
    ws.cell(row=linha_total, column=1).alignment = _centralizado()

    ws.cell(row=linha_total, column=2,
            value=f"=SUM(B5:B{ultima_linha_dados})").number_format = 'R$ #,##0.00'
    ws.cell(row=linha_total, column=2).font = _fonte_cabecalho()
    ws.cell(row=linha_total, column=2).fill = _fundo(COR_AZUL)
    ws.cell(row=linha_total, column=2).alignment = _centralizado()

  
    chart = BarChart()
    chart.type = "col"          
    chart.title = "Faturamento por Período"
    chart.y_axis.title = "R$"
    chart.x_axis.title = "Período"
    chart.style = 10
    chart.width = 20
    chart.height = 12

    dados = Reference(ws, min_col=2, min_row=4, max_row=4 + len(df))
    categorias = Reference(ws, min_col=1, min_row=5, max_row=4 + len(df))
    chart.add_data(dados, titles_from_data=True)
    chart.set_categories(categorias)

    ws.add_chart(chart, f"D4")

    _ajustar_colunas(ws, [18, 20, 5, 20])




def _aba_produtos(wb: Workbook, metricas: dict) -> None:
   
    ws = wb.create_sheet("Top Produtos")
    df = metricas["top_produtos"]

    _cabecalho_aba(ws, "Top Produtos", "Produtos com maior faturamento em transações aprovadas")

    _linha_cabecalho_tabela(ws, 4, ["#", "Produto", "Faturamento (R$)", "Unidades Vendidas"])

    for i, row in enumerate(df.itertuples(), start=1):
        linha = 4 + i
        _linha_dados(
            ws, linha,
            [i, row.produto, row.faturamento, int(row.quantidade_vendida)],
            alternada=i % 2 == 0
        )
        ws.cell(row=linha, column=3).number_format = 'R$ #,##0.00'

    _ajustar_colunas(ws, [6, 30, 22, 20])

def _aba_auditoria(wb: Workbook, df_suspeitos: pd.DataFrame) -> None:
    ws = wb.create_sheet("Auditoria")

    _cabecalho_aba(
        ws,
        " Auditoria — Transações Suspeitas",
        "Transações com número de cartão inválido identificadas pelo Algoritmo de Luhn"
    )

    if df_suspeitos.empty:
        ws.merge_cells("A4:G4")
        ws["A4"] = "Nenhuma transação suspeita identificada."
        ws["A4"].font = Font(name="Arial", bold=True, size=12, color="155724")
        ws["A4"].fill = _fundo(COR_VERDE)
        ws["A4"].alignment = _centralizado()
        return

    colunas = ["ID Transação", "Data", "Nº Cartão", "Valor (R$)",
               "Tipo Pagamento", "Status", "Motivo da Suspeita"]
    _linha_cabecalho_tabela(ws, 4, colunas)

    for i, row in enumerate(df_suspeitos.itertuples(), start=1):
        linha = 4 + i
        data_str = str(row.data)[:10] if hasattr(row, "data") else ""
        valores = [
            getattr(row, "id_transacao", ""),
            data_str,
            getattr(row, "numero_cartao", ""),
            getattr(row, "valor", ""),
            getattr(row, "tipo_pagamento", ""),
            getattr(row, "status", ""),
            getattr(row, "motivo_auditoria", ""),
        ]
        _linha_dados(ws, linha, valores, alternada=i % 2 == 0)

        for col in range(1, 8):
            ws.cell(row=linha, column=col).fill = _fundo(
                COR_VERMELHO if i % 2 == 0 else "FDE8E8"
            )
        ws.cell(row=linha, column=4).number_format = 'R$ #,##0.00'

    _ajustar_colunas(ws, [14, 14, 20, 16, 16, 12, 40])

def gerar_relatorio(
    metricas: dict,
    df_suspeitos: pd.DataFrame,
    df_validos: pd.DataFrame = None,
) -> bytes:
    wb = Workbook()

    _aba_resumo(wb, metricas)
    _aba_periodo(wb, metricas)
    _aba_produtos(wb, metricas)
    _aba_auditoria(wb, df_suspeitos)

    if df_validos is not None:
        _aba_verificadas(wb, df_validos)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return buffer.getvalue()

def _aba_verificadas(wb: Workbook, df_validos: pd.DataFrame) -> None:
    from brand_detector import enriquecer_dataframe

    ws = wb.create_sheet("✅ Transações Verificadas")
    df = enriquecer_dataframe(df_validos)

    _cabecalho_aba(
        ws,
        "✅ Transações Verificadas",
        "Transações com cartão válido pelo Algoritmo de Luhn — número mascarado por segurança"
    )

    colunas = ["ID Transação", "Data", "Bandeira", "Cartão (mascarado)",
               "Valor (R$)", "Tipo Pagamento", "Produto", "Status"]
    _linha_cabecalho_tabela(ws, 4, colunas)

    for i, row in enumerate(df.itertuples(), start=1):
        linha = 4 + i
        data_str = str(row.data)[:10] if hasattr(row, "data") else ""
        bandeira_txt = f"{getattr(row, 'bandeira_emoji', '')} {getattr(row, 'bandeira', '')}"
        valores = [
            getattr(row, "id_transacao", ""),
            data_str,
            bandeira_txt,
            getattr(row, "cartao_mascarado", ""),
            getattr(row, "valor", ""),
            getattr(row, "tipo_pagamento", ""),
            getattr(row, "produto", ""),
            getattr(row, "status", ""),
        ]
        _linha_dados(ws, linha, valores, alternada=i % 2 == 0)
        ws.cell(row=linha, column=5).number_format = 'R$ #,##0.00'

    _ajustar_colunas(ws, [14, 13, 18, 22, 15, 16, 28, 12])