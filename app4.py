import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

st.title("Comparação de Pagamentos com Condições")

# Upload de planilhas
file_a = st.sidebar.file_uploader("Upload Planilha A (Pagamentos Recebidos - SISTEMA)", type=["xlsx", "xls"])
file_b = st.sidebar.file_uploader("Upload Planilha B (Pagamentos Compensados - BANCO)", type=["xlsx", "xls"])

start_row_a = start_row_b = 0

if file_a:
    df_a_preview = pd.read_excel(file_a, nrows=15)
    st.write("Pré-visualização das primeiras 15 linhas da Planilha A:")
    st.dataframe(df_a_preview)
    start_row_a = st.sidebar.number_input("Informe o número da linha com o CABEÇALHO dos dados da Planilha A:", min_value=0, value=1)
    start_row_a += 1
    
if file_b:
    df_b_preview = pd.read_excel(file_b, nrows=15)
    st.write("Pré-visualização das primeiras 15 linhas da Planilha B:")
    st.dataframe(df_b_preview)
    start_row_b = st.sidebar.number_input("Informe o número da linha com o CABEÇALHO dos dados da Planilha B:", min_value=0, value=10)
    start_row_b += 1


if file_a and file_b:
    st.empty()
    # Ler as planilhas a partir da linha escolhida
    df_a = pd.read_excel(file_a, skiprows=start_row_a)
    df_b = pd.read_excel(file_b, skiprows=start_row_b)

    # remover as 2 primeiras linhas do df_a
    df_a_preview = df_a_preview.iloc[int(start_row_a):]
    st.write("Pré-visualização das linhas da Planilha A após seleção da linha inicial:")
    st.dataframe(df_a_preview)

    # remover as 10 primeiras linhas do df_b
    df_b_preview = df_b_preview.iloc[int(start_row_b):]
    st.write("Pré-visualização das linhas da Planilha B após seleção da linha inicial:")
    st.dataframe(df_b_preview)

    # Seleção das colunas relevantes
    colunas_a = st.sidebar.multiselect("Selecione as colunas da Planilha A", df_a.columns.tolist())
    colunas_b = st.sidebar.multiselect("Selecione as colunas da Planilha B", df_b.columns.tolist())
    
    
    if colunas_a and colunas_b:
        print(colunas_a)

        # Remover colunas não selecionadas
        #df_a.drop(df_a.columns.intersection([colunas_a]), axis=1, inplace=True)
        #df_b.drop(df_b.columns.intersection([colunas_b]), axis=1, inplace=True)
        
        # Dataframe apenas com as colunas selecionadas
        df_a = df_a[df_a.columns.intersection(colunas_a)]
        df_b = df_b[df_b.columns.intersection(colunas_b)]
        
        # Remover as linhas de df_a onde o valor da coluna Lançamento é nulo
        df_a.dropna(axis=0, thresh=3, inplace=True) # thresh=3 # mantem apenas no minimo 3 valores não nulos (non-NA), # how='any', 
        df_b.dropna(inplace=True)

        st.write("Colunas selecionadas para análise:")
        st.write(f"Planilha A: {colunas_a}")
        st.write(f"Planilha B: {colunas_b}")

        # Comparação das colunas selecionadas
        datetime_a = st.sidebar.selectbox("Selecione a coluna de datetime na Planilha A:", colunas_a, index=1)
        date_b = st.sidebar.selectbox("Selecione a coluna de data de recebimento na Planilha B:", colunas_b, index=3)
        time_b = st.sidebar.selectbox("Selecione a coluna de time na Planilha B:", colunas_b, index=4)
        valor_a = st.sidebar.selectbox("Selecione a coluna de valor na Planilha A:", colunas_a)
        valor_b = st.sidebar.selectbox("Selecione a coluna de valor na Planilha B:", colunas_b)


        # transforma o tipo da coluna datetime_a em datetime
        df_a['datetime_a'] = pd.to_datetime(df_a[datetime_a])
        # Combinar date e time na planilha B para criar a coluna datetime
        df_b['datetime_b'] = pd.to_datetime(df_b[date_b].astype(str) + ' ' + df_b[time_b].astype(str))


        df_a['checked'] = False
        df_b['checked'] = False

        # Definindo a condição de merge
        def merge_condition(row1, row2):
            time_diff = np.abs((row1[datetime_a] - row2['datetime_b']).total_seconds() / 60)
            value_diff = np.abs(row1[valor_a] - row2[valor_b])
            if value_diff == 0.0:
              print(time_diff, value_diff)
            # 45 é a diferença de tempo em minutos
            return time_diff <= 45 and value_diff == 0.0 and row1['checked'] == False and row2['checked'] == False


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

                    for c in df_b.columns:
                        merged_row[c] = row2[c]
                    # merged_row['Pagador'] = row2['pagador']
                    # merged_row['Valor'] = row2[valor_b]
                    # merged_row['Data'] = row2['datetime_b']

                    # merged_row['Hora'] = row2['hora recebimento']
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