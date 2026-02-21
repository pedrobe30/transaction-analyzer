import streamlit as st
import pandas as pd

from loader import load_file, FormatoNaoSuportadoError, ColunasFaltandoError
from validator import processar
from metrics import calcular_todas
from reporter import gerar_relatorio
from brand_detector import enriquecer_dataframe, badge_html, detectar_bandeira

st.set_page_config(
    page_title="Transaction Analyzer",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
    <style>
        /* Tipografia e espaçamento geral */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        /* Cabeçalho Apple-like: Simples, grande, alto contraste */
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            letter-spacing: -0.05em;
            margin-bottom: 0.2rem;
            color: var(--text-color);
        }
        .hero-subtitle {
            font-size: 1.2rem;
            color: var(--faded-text-color);
            margin-bottom: 2rem;
            font-weight: 400;
        }

        /* Cards de Métricas com bordas sutis e fundo adaptável */
        div[data-testid="stMetric"] {
            background-color: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            transition: transform 0.2s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
        }
        
        /* Botões mais arredondados estilo iOS */
        .stButton > button, .stDownloadButton > button {
            border-radius: 12px !important;
            font-weight: 600 !important;
            padding: 0.5rem 1rem !important;
            border: 1px solid rgba(128, 128, 128, 0.2) !important;
        }

        /* Oculta os índices das tabelas nativas de forma mais limpa */
        thead tr th:first-child {display:none}
        tbody th {display:none}
    </style>
""", unsafe_allow_html=True)


st.markdown('<div class="hero-title">Análise de Transações .</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Validação inteligente de transações. Rápido, seguro e preciso.</div>', unsafe_allow_html=True)


if "analise_feita" not in st.session_state:
    st.session_state["analise_feita"] = False

if not st.session_state["analise_feita"]:
    upload_col1, upload_col2, upload_col3 = st.columns([1, 2, 1])
    
    with upload_col2:
        st.markdown("### Selecione sua base de dados")
        arquivo_upload = st.file_uploader(
            label="Upload",
            type=["csv", "xlsx"],
            label_visibility="collapsed"
        )
        
        if arquivo_upload is not None:
            with st.spinner("Analisando dados..."):
                try:
                    df_bruto = load_file(arquivo_upload)
                    df_validos, df_suspeitos        = processar(df_bruto)
                    df_validos_enriquecido          = enriquecer_dataframe(df_validos)
                    metricas                        = calcular_todas(df_validos)
                    relatorio_bytes                 = gerar_relatorio(metricas, df_suspeitos, df_validos)

                    st.session_state["metricas"]               = metricas
                    st.session_state["df_suspeitos"]           = df_suspeitos
                    st.session_state["df_validos_enriquecido"] = df_validos_enriquecido
                    st.session_state["relatorio_bytes"]        = relatorio_bytes
                    st.session_state["analise_feita"]          = True
                    st.rerun() 
                except Exception as e:
                    st.error(f"Erro no processamento: {e}")

if st.session_state["analise_feita"]:
    metricas       = st.session_state["metricas"]
    df_suspeitos   = st.session_state["df_suspeitos"]
    df_enriquecido = st.session_state["df_validos_enriquecido"]
    relatorio_bytes= st.session_state["relatorio_bytes"]

    # --- Top Bar: Ações Rápidas ---
    col_vazia, col_btn1, col_btn2 = st.columns([6, 2, 2])
    with col_btn1:
        st.download_button(
            label="📥 Baixar Relatório",
            data=relatorio_bytes,
            file_name="relatorio_transacoes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with col_btn2:
        if st.button("🔄 Nova Análise", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)


    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Faturamento", f"R$ {metricas['faturamento_total']:,.2f}")
    m2.metric("Ticket Médio", f"R$ {metricas['ticket_medio']:,.2f}")
    m3.metric("Transações Aprovadas", metricas["total_aprovadas"])
    m4.metric(
        "Cartões Inválidos", 
        len(df_suspeitos), 
        delta="Fraude Detectada" if len(df_suspeitos) > 0 else "Seguro",
        delta_color="inverse"
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

    tab_geral, tab_produtos, tab_auditoria = st.tabs(["Visão Geral", "Performance de Produtos", "Auditoria e Segurança"])

    with tab_geral:
        st.markdown("### Dinâmica de Faturamento")
        col_graf, col_share = st.columns([2, 1], gap="large")
        
        with col_graf:
            df_periodo = metricas["faturamento_por_periodo"]
            if not df_periodo.empty:
               
                st.area_chart(
                    df_periodo.set_index("periodo")["faturamento"],
                    use_container_width=True,
                    color="#0055CC"
                )
        
        with col_share:
            st.markdown("#### Por Meio de Pagamento")
            df_pag = metricas["breakdown_pagamento"].copy()
            df_pag["faturamento"] = pd.to_numeric(df_pag["faturamento"], errors="coerce")
            
            st.dataframe(
                df_pag,
                column_config={
                    "tipo_pagamento": st.column_config.TextColumn("Método"),
                    "faturamento": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                    "percentual": st.column_config.ProgressColumn("Share", format="%.1f%%", min_value=0, max_value=100)
                },
                hide_index=True,
                use_container_width=True
            )

    with tab_produtos:
        st.markdown("### Top Produtos Vendidos")
        df_top = metricas["top_produtos"].copy()
        df_top["faturamento"] = pd.to_numeric(df_top["faturamento"], errors="coerce")
        df_top["quantidade_vendida"] = pd.to_numeric(df_top["quantidade_vendida"], errors="coerce")
        
        st.dataframe(
            df_top,
            column_config={
                "produto": st.column_config.TextColumn("Produto", width="medium"),
                "faturamento": st.column_config.NumberColumn("Receita Gerada", format="R$ %.2f"),
                "quantidade_vendida": st.column_config.ProgressColumn(
                    "Volume (Unidades)", 
                    format="%d", 
                    min_value=0, 
                    max_value=int(df_top["quantidade_vendida"].max()) if not df_top.empty else 100
                )
            },
            hide_index=True,
            use_container_width=True
        )

    with tab_auditoria:
        st.markdown("### Registro de Transações")
        
        if df_suspeitos.empty:
            st.success("Tudo certo! Nenhuma transação reprovada pelo algoritmo de Luhn.")
        else:
            st.error(f"⚠️ {len(df_suspeitos)} transações isoladas por falha de validação (Luhn).")
            with st.expander("Ver transações suspeitas"):
                st.dataframe(df_suspeitos, hide_index=True, use_container_width=True)
                
        st.markdown("#### Cartões Válidos Processados")
        df_exibir = df_enriquecido.copy()
        if "valor" in df_exibir.columns:
            df_exibir["valor"] = pd.to_numeric(df_exibir["valor"], errors="coerce")
            
        st.dataframe(
            df_exibir,
            column_config={
                "id_transacao": "ID",
                "data": "Data",
                "cartao_mascarado": "Cartão",
                "bandeira_emoji": "Bandeira",
                "bandeira": None, 
                "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                "tipo_pagamento": "Método",
                "status": "Status"
            },
            hide_index=True,
            use_container_width=True
        )

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Desenvolvido por **Pedro Bernardo** · 2026")