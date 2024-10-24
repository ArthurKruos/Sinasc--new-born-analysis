from dbfread import DBF
import pandas as pd
import os
diretorio_dbf = r'C:\Users\PICHAU\Desktop\menu\Estudos\Estudos UFPB\Tec. Pesquisa e Análise de Dados\Análise DATASUS SINASC\tratados\PB'

# Lista para armazenar DataFrames
dataframes = []

# Percorre todos os arquivos no diretório
for arquivo in os.listdir(diretorio_dbf):
    if arquivo.endswith('.dbf'):
        caminho_completo = os.path.join(diretorio_dbf, arquivo)
        
        # Lê o arquivo .dbf
        try:
            dbf = DBF(caminho_completo)
            df = pd.DataFrame(iter(dbf))  # Converte para DataFrame
            dataframes.append(df)  # Adiciona o DataFrame à lista
            print(f'Lido: {caminho_completo}')
        except Exception as e:
            print(f'Erro ao ler {caminho_completo}: {e}')

if dataframes:
    df_total = pd.concat(dataframes, ignore_index=True)
    print('Todos os dados concatenados com sucesso!')
else:
    print('Nenhum arquivo .dbf encontrado ou lido.')

df_total['DTNASC'] = pd.to_datetime(df_total['DTNASC'], format='%d%m%Y')

# Substituir vírgulas por pontos e remover espaços
df_total['PESO'] = df_total['PESO'].str.replace(',', '.').str.strip()

# Converter para float, forçando valores inválidos a serem NaN
df_total['PESO'] = pd.to_numeric(df_total['PESO'], errors='coerce')

# Agora você pode filtrar normalmente os bebês com peso menor ou igual a 2500
df_baixo_peso = df_total.loc[(df_total['PESO'] < 2500) & (df_total['PESO'] > 0)].reset_index()

# ANALISE DOS MUNICIPIOS DE RESIDENCIA
df_res = df_baixo_peso.loc[df_baixo_peso['CODMUNRES'].astype(str).str.startswith('25')]
media_peso_municipio_res = df_res.groupby('CODMUNRES')['PESO'].count().sort_values()

# Media da idade das mães que dão luz a bebês abaixo do peso:
df_baixo_peso['IDADEMAE'] = pd.to_numeric(df_baixo_peso['IDADEMAE'], errors='coerce')
print(df_baixo_peso['IDADEMAE'].mean())
print(df_baixo_peso['IDADEMAE'].median())

# Sexo do recém nascido
df_sexo = df_baixo_peso
sexo = df_sexo.groupby('SEXO')['PESO'].count().sort_values()

# Tipo de Gravidez (Tipo de gravidez: 1– Única; 2– Dupla; 3– Tripla ou mais; 9– Ignorado.)
df_grav = df_baixo_peso
tipo_gravidez = df_grav.groupby('GRAVIDEZ')['PESO'].count().sort_values()

# Análise pré-natal (Número de consultas de pré‐natal. Valores: 1– Nenhuma; 2– de 1 a 3; 3– de 4 a 6; 4– 7 e mais; 9– Ignorado. )
df_nat = df_baixo_peso
pre_natal = df_nat.groupby('CONSULTAS')['PESO'].count().sort_values()

# Tipo de Parto (Tipo de parto: 1– Vaginal; 2– Cesário; 9– Ignorado )
df_part = df_baixo_peso
contagem_parto = df_part.groupby('PARTO')['PESO'].count().sort_values()

# Apresenta Anomalia Congênita (Código da anomalia (CID 10) )
df_part = df_baixo_peso
anomalia = df_part.groupby('CODANOMAL')['PESO'].count().sort_values()

#Duração de gestação 
# (Semanas de gestação: 1– Menos de 22 semanas; 2– 22 a 27
# semanas; 3– 28 a 31 semanas; 4– 32 a 36 semanas; 5– 37 a 41
# semanas; 6– 42 semanas e mais; 9– Ignorado. )
df_part = df_baixo_peso
gestacao = df_part.groupby('GESTACAO')['PESO'].count().sort_values()

# Recorrencia de idades das mães
df_mae = df_baixo_peso
mae = df_mae.groupby('IDADEMAE')['PESO'].count().sort_values()

# taxa de nascimentos de bebês abaixo do peso Visão paraíba:
soma_nascidos_abaixo_peso = df_baixo_peso['index'].count()
soma_total_nascidos = df_total['LOCNASC'].count()
taxa_total_pb = (soma_nascidos_abaixo_peso/soma_total_nascidos)*100

# taxa de nascimentos de bebês abaixo do peso Visão municipal:
df_res = df_baixo_peso.loc[df_baixo_peso['CODMUNRES'].astype(str).str.startswith('25')]
df_total_res = df_total.loc[df_total['CODMUNRES'].astype(str).str.startswith('25')]
nascidos_abaixo_peso_por_municipio = df_res.groupby('CODMUNRES')['PESO'].count()
total_nascidos_por_municipio = df_total_res.groupby('CODMUNRES')['PESO'].count()
taxa_por_municipio = (nascidos_abaixo_peso_por_municipio / total_nascidos_por_municipio) * 100

#comentando