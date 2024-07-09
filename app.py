# streamlit run app.py

import streamlit as st
import pandas as pd

st.title("Comparação de Pagamentos")

# Upload de planilhas
file_a = st.file_uploader("Upload Planilha A (Pagamentos Recebidos)", type=["xlsx", "xls"])
file_b = st.file_uploader("Upload Planilha B (Pagamentos Compensados)", type=["xlsx", "xls"])

if file_a and file_b:
    # Ler as planilhas
    df_a = pd.read_excel(file_a)
    df_b = pd.read_excel(file_b)
    
    # remover as 2 primeiras linhas do df_a
    df_a = df_a.iloc[2:]

    # remover as 10 primeiras linhas do df_b
    df_b = df_b.iloc[10:]
    # Remover coluna 3 e 4 de df_a
    df_a.drop(df_a.columns[[2,3,5,9,13]], axis=1, inplace=True)


    #df_a.dropna(inplace=True)
    df_b.dropna(inplace=True)



    # renomear coluna do dataframe com os dados da linha 1
    df_a.columns = df_a.iloc[0]
    df_b.columns = df_b.iloc[0]

    # # Remover a primeira linha do dataframe
    df_a = df_a.iloc[1:]
    df_b = df_b.iloc[1:]

    # Remover as linhas de df_a onde o valor da coluna Lançamento é nulo
    df_a.dropna(subset=['Lançamento'], inplace=True)

    # Filtrar df_a com os pagamentos realizados do Grupo igual a VENDA CARTEIRA DIGITAL ou VENDA CARTÕES
    df_a = df_a[df_a['Grupo'].isin(['VENDA CARTEIRA DIGITAL', 'VENDA CARTÕES'])]

    # Passo 2: Exibir os dados
    # Exibe informações 
    st.write("Planilha A (Pagamentos Recebidos):")
    st.dataframe(df_a)

    st.write("Planilha B (Pagamentos Compensados):")
    st.dataframe(df_b)

    # # Passo 3: Realizar a comparação
    # # Supondo que a chave de pagamento em df_a é 'chave_pagamento_a' e em df_b é 'chave_pagamento_b'
    # chave_pagamento_a = 'C. Digital'  # Ajuste conforme a sua planilha
    # chave_pagamento_b = 'valor restante (R$)'  # Ajuste conforme a sua planilha

    # # # Criar uma coluna para indicar se o pagamento foi efetivado
    # # df_a['efetivado'] = df_a[chave_pagamento_a].apply(
    # #     lambda x: any(df_b[chave_pagamento_b].astype(str).str.contains(str(x), na=False))
    # # )

    # df_comparacao = df_a.merge(df_b, left_on=chave_pagamento_a, right_on=chave_pagamento_b, how='left', indicator=True)

    # pagamentos_efetivados = df_comparacao[df_comparacao['_merge'] == 'both']
    # pagamentos_nao_efetivados = df_comparacao[df_comparacao['_merge'] == 'left_only']


    # #pagamentos_efetivados = df_a[df_a['efetivado']]
    # #pagamentos_nao_efetivados = df_a[~df_a['efetivado']]

    # # Passo 4: Exibir os resultados
    # st.write(f"Pagamentos Efetivados: {len(pagamentos_efetivados)}")
    # st.write(f"Pagamentos Não Efetivados: {len(pagamentos_nao_efetivados)}")

    # st.write("Pagamentos Não Encontrados (Detalhes):")
    # st.dataframe(pagamentos_nao_efetivados)

    # st.write("Pagamentos Efetivados (Detalhes):")
    # st.dataframe(pagamentos_efetivados)


    # Passo 3: Realizar a comparação
    # Supondo que a coluna datetime em df_a é 'datetime_a', a coluna date em df_b é 'date_b', a coluna time em df_b é 'time_b'
    # e a coluna de valores em ambas é 'valor'
    datetime_a = 'Lançamento'  # Ajuste conforme a sua planilha
    date_b = 'data recebimento'  # Ajuste conforme a sua planilha
    time_b = 'hora recebimento'  # Ajuste conforme a sua planilha

    valor_b = 'valor restante (R$)'

    # transforma o tipo da coluna datetime_a em datetime
    df_a[datetime_a] = pd.to_datetime(df_a[datetime_a])

    # Definir uma tolerância para horários próximos (por exemplo, 30 minutos)
    tolerancia = pd.Timedelta(minutes=30)

    # Inicializar colunas de efetivação e índice correspondente
    df_a['efetivado'] = False
    df_a['indice_correspondente'] = None

    # Iterar sobre as linhas da Planilha A e encontr
    
    valor_b = 'valor restante (R$)'  # Ajuste conforme a sua planilha

    # Criar a coluna datetime na Planilha B
    df_b['datetime_b'] = pd.to_datetime(df_b[date_b].astype(str) + ' ' + df_b[time_b].astype(str))

    # Definir uma tolerância para horários próximos (por exemplo, 30 minutos)
    tolerancia = pd.Timedelta(minutes=30)

    # Inicializar colunas de efetivação e índice correspondente
    df_a['efetivado'] = False
    df_a['indice_correspondente'] = None

    #transformar tipo das colunas valor_a e valor_b em float
    df_a['C. Digital'] = df_a['C. Digital'].astype(float)
    df_a['Cartão'] = df_a['Cartão'].astype(float)
    df_b[valor_b] = df_b[valor_b].astype(float)
    
     
    print(df_a.dtypes)
    print(df_b.dtypes)

    # for row in df_a.itertuples():
    #     print(f'===>> {row}')

    # Iterar sobre as linhas da Planilha A e encontrar correspondentes na Planilha B
    for row_a in df_a.itertuples():
        # atribuir valor para valor_a baseado no valor de C. Digital. Se C. Digital > 0.0 usar o valor da coluna C. Digital, senão o valor da coluna Cartão
        valor_a = df_a['C. Digital'].apply(lambda x: 'C. Digital' if x > 0.0 else 'Cartão')
        # print('=====>: ', valor_a)
        correspondente = df_b[
            (df_b['datetime_b'].between(row_a[datetime_a] - tolerancia, row_a[datetime_a] + tolerancia)) &
            (df_b[valor_b] == row_a[valor_a]) # TODO: ver isso aqui ValueError: Can only compare identically-labeled Series objects
        ]
        
        if not correspondente.empty:
            df_a.at[int(row_a['Index']), 'efetivado'] = True
            df_a.at[int(row_a['Index']), 'indice_correspondente'] = correspondente.index[0]

    pagamentos_efetivados = df_a[df_a['efetivado']]
    pagamentos_nao_efetivados = df_a[~df_a['efetivado']]

    # Passo 4: Exibir os resultados
    st.write(f"Pagamentos Efetivados: {len(pagamentos_efetivados)}")
    st.write(f"Pagamentos Não Efetivados: {len(pagamentos_nao_efetivados)}")

    st.write("Pagamentos Não Efetivados (Detalhes):")
    st.dataframe(pagamentos_nao_efetivados)

    st.write("Pagamentos Efetivados (Detalhes):")
    st.dataframe(pagamentos_efetivados)