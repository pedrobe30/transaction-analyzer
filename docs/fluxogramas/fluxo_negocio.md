flowchart TD
    INICIO([▶ Início]):::evento

    subgraph USUARIO ["👤 Usuário"]
        U1[Faz upload do arquivo CSV ou Excel]:::atividade
        U2[Corrige o arquivo e tenta novamente]:::atividade
        U3[Visualiza KPIs na interface]:::atividade
        U4[Baixa o relatório Excel]:::atividade
    end

    subgraph SISTEMA ["⚙️ Sistema"]
        S1{Formato válido? .csv ou .xlsx}:::decisao
        S2{Colunas obrigatórias OK?}:::decisao
        S3[Valida cada cartão com Algoritmo de Luhn]:::atividade
        S4[Separa transações suspeitas para auditoria]:::atividade
        S5[Remove nulos e duplicados]:::atividade
        S6[Calcula métricas faturamento · ticket médio · aprovação]:::atividade
        S7[Gera relatório Excel com abas e gráficos]:::atividade
        E1[Exibe erro: formato não suportado]:::erro
        E2[Exibe erro: informa colunas faltando]:::erro
    end

    FIM([⏹ Fim]):::evento

    INICIO --> U1
    U1 --> S1

    S1 -- ❌ Não --> E1
    E1 --> U2
    U2 --> U1

    S1 -- ✅ Sim --> S2

    S2 -- ❌ Não --> E2
    E2 --> FIM

    S2 -- ✅ Sim --> S3
    S3 --> S4
    S4 --> S5
    S5 --> S6
    S6 --> S7
    S7 --> U3
    U3 --> U4
    U4 --> FIM

    classDef atividade fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f,rx:8
    classDef decisao fill:#fef9c3,stroke:#eab308,color:#713f12
    classDef erro fill:#fee2e2,stroke:#ef4444,color:#7f1d1d,rx:8
    classDef evento fill:#003399,stroke:#003399,color:#ffffff,rx:20