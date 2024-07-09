import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

st.title("Comparação de Pagamentos")

# Upload de planilhas
file_a = st.file_uploader("Upload Planilha A (Pagamentos Recebidos)", type=["xlsx", "xls"])
file_b = st.file_uploader("Upload Planilha B (Pagamentos Compensados)", type=["xlsx", "xls"])

if file_a and file_b:
    # Ler as planilhas
    df_a = pd.read_excel(file_a)
    df_b = pd.read_excel(file_b)

    # Tratamento de Planilhas
    # remover as 2 primeiras linhas do df_a
    df_a = df_a.iloc[2:]
    # remover as 10 primeiras linhas do df_b
    df_b = df_b.iloc[10:]
    # Remover coluna 3 e 4 de df_a
    df_a.drop(df_a.columns[[2,3,5,9,13,14]], axis=1, inplace=True)
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
    df_a = df_a[df_a['Grupo'].isin(['VENDA CARTEIRA DIGITAL', 'ZZZ-VENDA CARTÕES'])]
    df_a['checked'] = False

    df_b['checked'] = False

    # Supondo que a chave de pagamento em df_a é 'chave_pagamento_a' e em df_b é 'chave_pagamento_b'
    # chave_pagamento_a = 'chave_pagamento_a'  # Ajuste conforme a sua planilha
    # chave_pagamento_b = 'Identificado Pagamento'  # Ajuste conforme a sua planilha
    valor_a = 'C. Digital'  # Ajuste conforme a sua planilha
    valor_b = 'valor restante (R$)'  # Ajuste conforme a sua planilha
    datetime_a = 'Lançamento'  # Ajuste conforme a sua planilha
    date_b = 'data recebimento'  # Ajuste conforme a sua planilha
    time_b = 'hora recebimento'  # Ajuste conforme a sua planilha

    #transformar tipo das colunas valor_a e valor_b em float
    df_a['C. Digital'] = df_a['C. Digital'].astype(float)
    df_a['Cartão'] = df_a['Cartão'].astype(float)
    df_b[valor_b] = df_b[valor_b].astype(float)
    
    # transforma o tipo da coluna datetime_a em datetime
    df_a[datetime_a] = pd.to_datetime(df_a[datetime_a])
    # Combinar date e time na planilha B para criar a coluna datetime
    df_b['datetime_b'] = pd.to_datetime(df_b[date_b].astype(str) + ' ' + df_b[time_b].astype(str))


    # Definindo a condição de merge
    def merge_condition(row1, row2):
        time_diff = np.abs((row1[datetime_a] - row2['datetime_b']).total_seconds() / 60)
        value_diff = np.abs(row1[valor_a] - row2[valor_b])
        # Se a diferença de tempo for menor ou igual a 45 minutos e checked não estiver marcado, então retorna True
        return value_diff == 0.0 and time_diff <= 45 and row1['checked'] == False and row2['checked'] == False


    # Realizando o merge
    merged_data = []

    for i, row1 in df_a.iterrows():
        for j, row2 in df_b.iterrows():
            if row2['checked'] == False:
              if merge_condition(row1, row2):
                # print(row1.values, row2.values)
                # Marcar a row2 como já verificada para evitar duplicidade
                df_b.loc[j, 'checked'] = True
                df_a.loc[i, 'checked'] = True
                # Criar uma nova coluna para marcar a relação entre as duas planilhas
                merged_row = row1.copy()
                #merged_row['check'] = True
                merged_row['Pagador'] = row2['pagador']
                merged_row['Valor'] = row2[valor_b]
                merged_row['Data'] = row2['datetime_b']
                merged_row['Hora'] = row2['hora recebimento']
                merged_data.append(merged_row)
                break

    # Convertendo para dataframe final
    merged_df = pd.DataFrame(merged_data)

    print(merged_df)

    # Mostrar DataFrame
    st.write("Planilha A (Pagamentos Recebidos):")
    st.dataframe(df_a)
    st.write(f"Total: {len(df_a)}")

    st.write("Planilha B (Pagamentos Compensados):")
    st.dataframe(df_b)
    st.write(f"Total: {len(df_b)}")

    st.write("CONSILIAÇÃO:")
    st.dataframe(merged_df)

    pagamentos_efetivados = df_a[df_a['checked']]
    pagamentos_nao_efetivados = df_a[~df_a['checked']]

    # Exibir os resultados
    st.write(f"Pagamentos Encontrados: {len(pagamentos_efetivados)}")
    st.write(f"Pagamentos Não Encontrados: {len(pagamentos_nao_efetivados)}")

    st.write("Pagamentos Não Encontrados (Detalhes):")
    st.dataframe(pagamentos_nao_efetivados)

    st.write("Pagamentos Encontrados (Detalhes):")
    st.dataframe(pagamentos_efetivados)