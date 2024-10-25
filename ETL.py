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
                dbf = DBF(caminho_completo, encoding='utf-8')
                df = pd.DataFrame(iter(dbf))
                dataframes.append(df)
            except Exception as e:
                st.error(f'Erro ao ler o arquivo {arquivo}: {e}')
    
    if dataframes:
        df_total = pd.concat(dataframes, ignore_index=True)
        return df_total
    else:
        st.warning('Nenhum arquivo .dbf encontrado ou lido.')
        return None

# Função para pré-processamento dos dados
def preprocess_data(df):
    try:
        df['DTNASC'] = pd.to_datetime(df['DTNASC'], format='%d%m%Y', errors='coerce')
        df['PESO'] = pd.to_numeric(df['PESO'].str.replace(',', '.').str.strip(), errors='coerce')
        df_baixo_peso = df[(df['PESO'] < 2500) & (df['PESO'] > 0)].reset_index(drop=True)
        return df_baixo_peso
    except Exception as e:
        st.error(f"Erro durante o pré-processamento: {e}")
        return None

# Função para visualização dos dados
def display_analysis(df_baixo_peso, df_total):
    st.subheader('Análise dos Nascimentos com Peso Abaixo de 2500g')
    st.write(f'Total de Nascimentos Abaixo do Peso: {len(df_baixo_peso)}')

    # Média e Mediana da Idade das Mães
    st.write(f'Média da Idade das Mães: {df_baixo_peso["IDADEMAE"].mean():.2f}')
    st.write(f'Mediana da Idade das Mães: {df_baixo_peso["IDADEMAE"].median():.2f}')

    # Gráficos
    st.subheader('Distribuição de Sexo dos Recém-Nascidos')
    st.bar_chart(df_baixo_peso['SEXO'].value_counts())

    st.subheader('Tipo de Gravidez')
    st.bar_chart(df_baixo_peso['GRAVIDEZ'].value_counts())

    st.subheader('Consultas de Pré-Natal')
    st.bar_chart(df_baixo_peso['CONSULTAS'].value_counts())

    st.subheader('Tipo de Parto')
    st.bar_chart(df_baixo_peso['PARTO'].value_counts())

    # Taxa de Nascimentos Abaixo do Peso
    taxa_total_pb = (len(df_baixo_peso) / len(df_total)) * 100
    st.write(f'Taxa Total de Nascimentos Abaixo do Peso: {taxa_total_pb:.2f}%')

    # Visualização por Município
    st.subheader('Taxa de Nascimentos Abaixo do Peso por Município')
    df_res = df_baixo_peso[df_baixo_peso['CODMUNRES'].astype(str).str.startswith('25')]
    taxa_por_municipio = (df_res.groupby('CODMUNRES')['PESO'].count() / 
                          df_total[df_total['CODMUNRES'].astype(str).str.startswith('25')].groupby('CODMUNRES')['PESO'].count()) * 100
    st.bar_chart(taxa_por_municipio.dropna())

# Configuração da interface
st.title('Análise de Dados de Nascimentos')

# Input para o diretório dos arquivos .dbf
diretorio_dbf = st.text_input('Insira o caminho do diretório dos arquivos .dbf:', 
                            value=r'C:\Users\PICHAU\Desktop\menu\Estudos\Estudos UFPB\Tec. Pesquisa e Análise de Dados\Análise DATASUS SINASC\Ignorar\tratados\PB')

# Verificar se o diretório existe
if os.path.exists(diretorio_dbf):
    df_total = load_data(diretorio_dbf)
    
    if df_total is not None:
        df_baixo_peso = preprocess_data(df_total)
        
        if df_baixo_peso is not None:
            display_analysis(df_baixo_peso, df_total)
else:
    st.error('Diretório não encontrado. Verifique o caminho especificado.')