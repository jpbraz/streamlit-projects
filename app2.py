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
    df_a = df_a[df_a['Grupo'].isin(['VENDA CARTEIRA DIGITAL', 'VENDA CARTÕES'])]
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
        if value_diff == 0.0:
          print(time_diff, value_diff)
        
        return time_diff <= 30000 and value_diff == 0.0 and row1['checked'] == False and row2['checked'] == False


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

    # # Criar uma coluna para indicar se o pagamento foi efetivado
    # def match_payment(row_a, df_b):
    #     # atribuir valor para valor_a baseado no valor de C. Digital. Se C. Digital > 0.0 usar o valor da coluna C. Digital, senão o valor da coluna Cartão     
    #     valor_a = 'Cartão' if row_a['C. Digital'] == '0.00' else 'C. Digital'
    #     timestamp_a = round(row_a[datetime_a].timestamp())
    #     # timestamp_b = round(df_b['datetime_b'] .timestamp())
    #     # print(f'{timestamp_a} - {timestamp_b} - {timedelta(minutes=40)}')
    #     mask = (
    #         #(abs(pd.to_datetime(row_a[datetime_a]) - df_b['datetime_b']) <= timedelta(minutes=40)) &
    #         (df_b[valor_b] == row_a[valor_a])
    #     )
    #     # imprimir o valor de datetime_b correspondente ao mask
    #     if mask.any():
    #       print(df_b[mask]['datetime_b'], df_b[mask][valor_b], df_b[mask]['pagador'])
    #     # return df_b[mask]['datetime_b'].values[0] if mask.any() else None  # retorna a primeira data de datetime_b que corresponde ao mask
    #     # return df_b[mask][valor_b].values[0] if mask.any() else 0  # retorna 0 se não houver um match no df_b
    #     # return df_b[mask][valor_b].values[0] if mask.any() else pd.NaT  # retorna NaT se não houver um match no df_b
        
    #     return mask.any()
    
    # # Função para verificar se dois pagamentos são correspondentes
    # def match_payment(row_a, df_b):
    #     mask = (
    #         #(abs(row_a[datetime_a] - df_b['datetime_b']) <= timedelta(minutes=30)) &
    #         (df_b[valor_b] == row_a[valor_a])
    #     )
    #     return df_b[mask]

    # # Aplicar a função de correspondência
    # df_a['efetivado'] = df_a.apply(lambda row: match_payment(row, df_b), axis=1)

    


    # Mostrar DataFrame
    st.write("Planilha A (Pagamentos Recebidos):")
    st.dataframe(df_a)

    st.write("Planilha B (Pagamentos Compensados):")
    st.dataframe(df_b)

    st.write("MERGED:")
    st.dataframe(merged_df)

    pagamentos_efetivados = df_a[df_a['checked']]
    pagamentos_nao_efetivados = df_a[~df_a['checked']]

    # Exibir os resultados
    st.write(f"Pagamentos Efetivados: {len(pagamentos_efetivados)}")
    st.write(f"Pagamentos Não Efetivados: {len(pagamentos_nao_efetivados)}")

    st.write("Pagamentos Não Efetivados (Detalhes):")
    st.dataframe(pagamentos_nao_efetivados)

    st.write("Pagamentos Efetivados (Detalhes):")
    st.dataframe(pagamentos_efetivados)