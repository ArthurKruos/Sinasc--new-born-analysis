import streamlit as st
import pandas as pd
from dbfread import DBF
import os

# Função para carregar dados
def load_data(diretorio_dbf):
    dataframes = []
    for arquivo in os.listdir(diretorio_dbf):
        if arquivo.endswith('.dbf'):
            caminho_completo = os.path.join(diretorio_dbf, arquivo)
            try:
                dbf = DBF(caminho_completo)
                df = pd.DataFrame(iter(dbf))
                dataframes.append(df)
            except Exception as e:
                st.error(f'Erro ao ler {caminho_completo}: {e}')
    
    if dataframes:
        df_total = pd.concat(dataframes, ignore_index=True)
        return df_total
    else:
        st.warning('Nenhum arquivo .dbf encontrado ou lido.')
        return None

# Configuração da interface
st.title('Análise de Dados de Nascimentos')

# Insira seu caminho aqui diretamente
diretorio_dbf = r'C:\Users\PICHAU\Desktop\menu\Estudos\Estudos UFPB\Tec. Pesquisa e Análise de Dados\Análise DATASUS SINASC\Ignorar\tratados\PB'


# Verificar se o diretório existe
if os.path.exists(diretorio_dbf):
    df_total = load_data(diretorio_dbf)
    
    if df_total is not None:
        # Pré-processamento
        df_total['DTNASC'] = pd.to_datetime(df_total['DTNASC'], format='%d%m%Y')
        df_total['PESO'] = df_total['PESO'].str.replace(',', '.').str.strip()
        df_total['PESO'] = pd.to_numeric(df_total['PESO'], errors='coerce')
        
        df_baixo_peso = df_total.loc[(df_total['PESO'] < 2500) & (df_total['PESO'] > 0)].reset_index()

        # Análises e visualizações
        st.subheader('Análise dos Nascimentos com Peso Abaixo de 2500g')
        st.write(f'Total de Nascimentos Abaixo do Peso: {len(df_baixo_peso)}')
        
        # Média e Mediana da Idade das Mães
        st.write(f'Média da Idade das Mães: {df_baixo_peso["IDADEMAE"].mean():.2f}')
        st.write(f'Mediana da Idade das Mães: {df_baixo_peso["IDADEMAE"].median():.2f}')
        
        # Gráficos
        st.subheader('Distribuição de Sexo dos Recém Nascidos')
        sexo_count = df_baixo_peso['SEXO'].value_counts()
        st.bar_chart(sexo_count)

        st.subheader('Tipo de Gravidez')
        tipo_grav_count = df_baixo_peso['GRAVIDEZ'].value_counts()
        st.bar_chart(tipo_grav_count)

        st.subheader('Consultas de Pré-Natal')
        pre_natal_count = df_baixo_peso['CONSULTAS'].value_counts()
        st.bar_chart(pre_natal_count)

        st.subheader('Tipo de Parto')
        contagem_parto = df_baixo_peso['PARTO'].value_counts()
        st.bar_chart(contagem_parto)

        # Taxa de Nascimentos Abaixo do Peso
        soma_nascidos_abaixo_peso = len(df_baixo_peso)
        soma_total_nascidos = len(df_total)
        taxa_total_pb = (soma_nascidos_abaixo_peso / soma_total_nascidos) * 100
        st.write(f'Taxa Total de Nascimentos Abaixo do Peso: {taxa_total_pb:.2f}%')

        # Visualização por Município
        st.subheader('Taxa de Nascimentos Abaixo do Peso por Município')
        df_res = df_baixo_peso[df_baixo_peso['CODMUNRES'].astype(str).str.startswith('25')]
        taxa_por_municipio = df_res.groupby('CODMUNRES')['PESO'].count() / df_total[df_total['CODMUNRES'].astype(str).str.startswith('25')].groupby('CODMUNRES')['PESO'].count() * 100
        st.bar_chart(taxa_por_municipio)

else:
    st.error('Diretório não encontrado. Verifique o caminho especificado.')
