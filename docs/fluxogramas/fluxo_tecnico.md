flowchart TD
    ARQUIVO(["📁 arquivo .csv ou .xlsx envio do usuário"]):::entrada

    subgraph LOADER ["📥 loader.py — Carregamento"]
        L1{Arquivo existe?}:::decisao
        L2{Formato .csv ou .xlsx?}:::decisao
        L3{Colunas obrigatórias OK?}:::decisao
        L4[Retorna DataFrame com colunas normalizadas]:::ok
        LE1[FileNotFoundError]:::erro
        LE2[FormatoNaoSuportadoError]:::erro
        LE3[ColunasFaltandoError]:::erro
    end

    subgraph VALIDATOR ["🔍 validator.py — Validação e Limpeza"]
        V1[Remove duplicados e normaliza tipos]:::atividade
        V2[Executa Algoritmo de Luhn em cada cartão]:::atividade
        V3{Cartão válido?}:::decisao
        V4[(df_validos ✅ prontos para análise)]:::dados
        V5[(df_suspeitos ⚠️ cartões inválidos)]:::auditoria
    end

    subgraph METRICS ["📊 metrics.py — Cálculo de KPIs"]
        M1[Faturamento total e por período]:::atividade
        M2[Ticket médio]:::atividade
        M3[Taxa de aprovação vs recusa]:::atividade
        M4[Top 5 produtos]:::atividade
        M5[Breakdown por tipo de pagamento]:::atividade
    end

    subgraph REPORTER ["📤 reporter.py — Geração do Relatório"]
        R1[Aba: Resumo Executivo KPIs + formatação visual]:::atividade
        R2[Aba: Faturamento por período + gráfico]:::atividade
        R3[Aba: Top Produtos]:::atividade
        R4[Aba: Auditoria transações suspeitas]:::atividade
    end

    SAIDA(["📊 relatório_transacoes.xlsx pronto para download"]):::saida

    ARQUIVO --> L1
    L1 -- ❌ --> LE1
    L1 -- ✅ --> L2
    L2 -- ❌ --> LE2
    L2 -- ✅ --> L3
    L3 -- ❌ --> LE3
    L3 -- ✅ --> L4

    L4 --> V1
    V1 --> V2
    V2 --> V3
    V3 -- ✅ válido --> V4
    V3 -- ❌ suspeito --> V5

    V4 --> M1 & M2 & M3 & M4 & M5

    M1 & M2 & M3 & M4 & M5 --> R1
    R1 --> R2 --> R3
    V5 --> R4

    R1 & R2 & R3 & R4 --> SAIDA

    classDef entrada fill:#f3e8ff,stroke:#a855f7,color:#3b0764,rx:20
    classDef saida fill:#dcfce7,stroke:#22c55e,color:#14532d,rx:20
    classDef atividade fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f,rx:6
    classDef decisao fill:#fef9c3,stroke:#eab308,color:#713f12
    classDef erro fill:#fee2e2,stroke:#ef4444,color:#7f1d1d,rx:6
    classDef ok fill:#dcfce7,stroke:#22c55e,color:#14532d,rx:6
    classDef dados fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    classDef auditoria fill:#fef9c3,stroke:#eab308,color:#713f12
