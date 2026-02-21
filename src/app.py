"""
app.py — Interface web do Elo Transaction Analyzer.

Como rodar:
    streamlit run src/app.py
"""

import streamlit as st
import pandas as pd

from loader import load_file, FormatoNaoSuportadoError, ColunasFaltandoError
from validator import processar
from metrics import calcular_todas
from reporter import gerar_relatorio
from brand_detector import enriquecer_dataframe, badge_html, detectar_bandeira

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Elo Transaction Analyzer",
    page_icon="💳",
    layout="wide",
)

# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
    <style>
        .stApp { background-color: #F0F4FF; }

        .header-container {
            background: linear-gradient(135deg, #003399 0%, #0055CC 100%);
            padding: 2rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(0, 51, 153, 0.25);
        }
        .header-title {
            color: #FFFFFF;
            font-size: 2.4rem;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .header-subtitle { color: #A8C4FF; font-size: 1rem; margin-top: 0.4rem; }
        .header-badge {
            display: inline-block;
            background: rgba(255,255,255,0.15);
            color: white;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 0.78rem;
            margin-right: 6px;
            margin-top: 0.8rem;
        }

        .section-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid #E8EEF8;
        }
        .section-title { color: #003399; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.2rem; }
        .section-desc  { color: #888888; font-size: 0.85rem; margin-bottom: 0; }

        div[data-testid="stMetric"] {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid #E8EEF8;
        }
        .stButton > button {
            background: #003399 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        .stDownloadButton > button {
            background: #003399 !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }

        .card-bandeira {
            background: white;
            border-radius: 10px;
            padding: 0.8rem 1.2rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.07);
            border: 1px solid #E8EEF8;
            text-align: center;
        }
        .card-bandeira-nome { font-weight: 700; font-size: 0.85rem; color: #333; margin-top: 4px; }
        .card-bandeira-qtd  { font-size: 1.4rem; font-weight: 800; color: #003399; }

        .footer {
            text-align: center;
            color: #AAAAAA;
            font-size: 0.78rem;
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #E8EEF8;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# CABEÇALHO
# ============================================================

st.markdown("""
    <div class="header-container">
        <p class="header-title">💳 Elo Transaction Analyzer</p>
        <p class="header-subtitle">
            Análise inteligente de transações com validação de cartões pelo Algoritmo de Luhn
        </p>
        <span class="header-badge">🔍 Validação Luhn</span>
        <span class="header-badge">🏷️ Detector de Bandeiras</span>
        <span class="header-badge">📊 Métricas em tempo real</span>
        <span class="header-badge">📥 Relatório Excel</span>
        <span class="header-badge">⚠️ Auditoria de suspeitas</span>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# SEÇÃO 1 — UPLOAD
# ============================================================

st.markdown("""
    <div class="section-card">
        <p class="section-title">📁 Passo 1 — Faça o upload do arquivo de transações</p>
        <p class="section-desc">
            Formatos aceitos: <strong>CSV</strong> ou <strong>Excel (.xlsx)</strong> &nbsp;·&nbsp;
            Colunas obrigatórias: id_transacao, data, numero_cartao, valor, tipo_pagamento, produto, status
        </p>
    </div>
""", unsafe_allow_html=True)

arquivo_upload = st.file_uploader(
    label="Selecione ou arraste o arquivo aqui",
    type=["csv", "xlsx"],
    help="Máximo recomendado: 10.000 linhas.",
    label_visibility="collapsed",
)

# ============================================================
# LÓGICA PRINCIPAL
# ============================================================

if arquivo_upload is not None:

    with st.spinner("⏳ Carregando arquivo..."):
        try:
            df_bruto = load_file(arquivo_upload)
        except FormatoNaoSuportadoError as e:
            st.error(f"❌ Formato não suportado: {e}")
            st.stop()
        except ColunasFaltandoError as e:
            st.error(f"❌ Arquivo inválido: {e}")
            st.info("💡 Verifique se todas as colunas obrigatórias estão presentes.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Erro inesperado: {e}")
            st.stop()

    st.success(f"✅ Arquivo **{arquivo_upload.name}** carregado — **{len(df_bruto)} linhas** encontradas.")

    with st.expander("🔍 Pré-visualização dos dados brutos", expanded=False):
        st.dataframe(df_bruto.head(8), use_container_width=True)
        st.caption(f"Exibindo 8 de {len(df_bruto)} linhas · Colunas: {', '.join(df_bruto.columns.tolist())}")

    st.divider()

    # ============================================================
    # SEÇÃO 2 — ANÁLISE
    # ============================================================

    st.markdown("""
        <div class="section-card">
            <p class="section-title">⚙️ Passo 2 — Analise as transações</p>
            <p class="section-desc">
                O sistema irá: validar os cartões com Algoritmo de Luhn · detectar a bandeira de cada cartão ·
                limpar os dados · calcular métricas · gerar relatório Excel com 5 abas.
            </p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Analisar Transações", type="primary", use_container_width=True):
        with st.spinner("🔍 Validando cartões, detectando bandeiras e calculando métricas..."):
            try:
                df_validos, df_suspeitos        = processar(df_bruto)
                df_validos_enriquecido          = enriquecer_dataframe(df_validos)
                metricas                        = calcular_todas(df_validos)
                relatorio_bytes                 = gerar_relatorio(metricas, df_suspeitos, df_validos)

                st.session_state["metricas"]               = metricas
                st.session_state["df_suspeitos"]           = df_suspeitos
                st.session_state["df_validos_enriquecido"] = df_validos_enriquecido
                st.session_state["relatorio_bytes"]        = relatorio_bytes
                st.session_state["analise_feita"]          = True
            except Exception as e:
                st.error(f"❌ Erro durante a análise: {e}")
                st.stop()

    # ============================================================
    # SEÇÃO 3 — RESULTADOS
    # ============================================================

    if st.session_state.get("analise_feita"):
        metricas               = st.session_state["metricas"]
        df_suspeitos           = st.session_state["df_suspeitos"]
        df_enriquecido         = st.session_state["df_validos_enriquecido"]
        relatorio_bytes        = st.session_state["relatorio_bytes"]

        st.divider()
        st.markdown('<p class="section-title" style="font-size:1.3rem">📊 Passo 3 — Resultados</p>', unsafe_allow_html=True)

        # --- KPIs ---
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("💰 Faturamento Total",  f"R$ {metricas['faturamento_total']:,.2f}")
        with c2:
            st.metric("🎯 Ticket Médio",       f"R$ {metricas['ticket_medio']:,.2f}")
        with c3:
            st.metric("✅ Taxa de Aprovação",  f"{metricas['taxa_aprovacao']}%")

        st.markdown("<br>", unsafe_allow_html=True)

        c4, c5, c6 = st.columns(3)
        with c4:
            st.metric("📦 Total de Transações", metricas["total_transacoes"])
        with c5:
            st.metric("✔️ Aprovadas",           metricas["total_aprovadas"])
        with c6:
            st.metric(
                "⚠️ Suspeitas (Luhn inválido)",
                len(df_suspeitos),
                delta=f"-{len(df_suspeitos)}" if len(df_suspeitos) > 0 else None,
                delta_color="inverse",
            )

        st.divider()

        # --- Gráfico + Breakdown ---
        col_graf, col_pag = st.columns([2, 1])

        with col_graf:
            st.markdown("**📅 Faturamento por Período**")
            df_periodo = metricas["faturamento_por_periodo"]
            if not df_periodo.empty:
                st.bar_chart(
                    df_periodo.set_index("periodo")["faturamento"],
                    use_container_width=True,
                    color="#003399",
                )
            else:
                st.info("Sem dados de faturamento por período.")

        with col_pag:
            st.markdown("**💳 Breakdown por Pagamento**")
            df_pag = metricas["breakdown_pagamento"].copy()
            df_pag["faturamento"] = pd.to_numeric(df_pag["faturamento"], errors="coerce")
            df_pag["percentual"]  = pd.to_numeric(df_pag["percentual"],  errors="coerce")
            st.dataframe(
                df_pag.style.format({"faturamento": "R$ {:,.2f}", "percentual": "{:.2f}%"}),
                use_container_width=True, hide_index=True,
            )

        st.divider()

        # --- Top Produtos ---
        st.markdown("**🏆 Top Produtos**")
        df_top = metricas["top_produtos"].copy()
        df_top["faturamento"]        = pd.to_numeric(df_top["faturamento"],        errors="coerce")
        df_top["quantidade_vendida"] = pd.to_numeric(df_top["quantidade_vendida"], errors="coerce")
        st.dataframe(
            df_top.style.format({"faturamento": "R$ {:,.2f}", "quantidade_vendida": "{:.0f}"}),
            use_container_width=True, hide_index=True,
        )

        st.divider()

        # ============================================================
        # SEÇÃO 4 — TRANSAÇÕES VERIFICADAS COM BANDEIRAS
        # ============================================================

        st.markdown("**✅ Transações Verificadas — Cartões Válidos por Bandeira**")

        # Mini-painel com contagem por bandeira
        if not df_enriquecido.empty:
            contagem = df_enriquecido["bandeira"].value_counts()
            bandeira_cols = st.columns(min(len(contagem), 5))
            for i, (nome, qtd) in enumerate(contagem.items()):
                info = detectar_bandeira(
                    df_enriquecido[df_enriquecido["bandeira"] == nome]["numero_cartao"].iloc[0]
                )
                with bandeira_cols[i % len(bandeira_cols)]:
                    st.markdown(
                        f'<div class="card-bandeira">'
                        f'<div style="font-size:1.8rem">{info["emoji"]}</div>'
                        f'<div class="card-bandeira-nome">{nome}</div>'
                        f'<div class="card-bandeira-qtd">{qtd}</div>'
                        f'<div style="font-size:0.72rem;color:#999">transações</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            # Tabela com badges HTML inline
            colunas_exibir = ["id_transacao", "data", "cartao_mascarado",
                               "bandeira_emoji", "bandeira", "valor", "tipo_pagamento", "status"]
            colunas_disponiveis = [c for c in colunas_exibir if c in df_enriquecido.columns]

            df_exibir = df_enriquecido[colunas_disponiveis].copy()
            df_exibir.rename(columns={
                "id_transacao":    "ID",
                "data":            "Data",
                "cartao_mascarado":"Cartão",
                "bandeira_emoji":  "🏷️",
                "bandeira":        "Bandeira",
                "valor":           "Valor (R$)",
                "tipo_pagamento":  "Pagamento",
                "status":          "Status",
            }, inplace=True)

            if "Valor (R$)" in df_exibir.columns:
                df_exibir["Valor (R$)"] = pd.to_numeric(df_exibir["Valor (R$)"], errors="coerce")

            st.dataframe(
                df_exibir.style.format({"Valor (R$)": "R$ {:,.2f}"}),
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        # ============================================================
        # SEÇÃO 5 — TRANSAÇÕES SUSPEITAS
        # ============================================================

        st.markdown("**⚠️ Auditoria — Transações Suspeitas (Luhn inválido)**")

        if df_suspeitos.empty:
            st.success("✅ Nenhuma transação suspeita. Todos os cartões passaram na validação Luhn.")
        else:
            st.warning(
                f"**{len(df_suspeitos)} transação(ões)** com cartão inválido identificadas. "
                f"Separadas do faturamento e disponíveis na aba **Auditoria** do relatório Excel."
            )
            st.dataframe(df_suspeitos, use_container_width=True, hide_index=True)

        st.divider()

        # ============================================================
        # SEÇÃO 6 — DOWNLOAD
        # ============================================================

        st.markdown('<p class="section-title" style="font-size:1.2rem">📥 Passo 4 — Baixar Relatório</p>', unsafe_allow_html=True)
        st.caption("O relatório contém **5 abas**: Resumo Executivo · Faturamento por Período · Top Produtos · Transações Verificadas · Auditoria")

        st.download_button(
            label="⬇️ Baixar Relatório Excel (.xlsx)",
            data=relatorio_bytes,
            file_name="relatorio_transacoes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )

# ============================================================
# RODAPÉ
# ============================================================

st.markdown("""
    <div class="footer">
        Elo Transaction Analyzer · Desenvolvido por Pedro Bernardo · 2026<br>
        Python · Pandas · openpyxl · Streamlit · Algoritmo de Luhn · Detector de Bandeiras
    </div>
""", unsafe_allow_html=True)