import pandas as pd
import os

def limpar_textos(serie):
    """
    Função auxiliar para padronizar os nomes dos municípios.
    Converte os textos para string, remove espaços extras (no início e no fim) 
    e transforma tudo em letras maiúsculas.
    """
    return serie.astype(str).str.strip().str.upper()

def remover_colunas_indice(df):
    """
    Remove colunas criadas automaticamente quando um CSV é salvo com o índice do pandas.
    Essas colunas geralmente aparecem como 'Unnamed: 0' e não fazem parte dos atributos reais.
    """
    colunas_indice = [col for col in df.columns if col.startswith('Unnamed:')]
    return df.drop(columns=colunas_indice, errors='ignore')

def normalizar_data_nascimento(df):
    """
    Padroniza a coluna 'dataNascimento' para o formato dd/mm/aaaa.
    O arquivo original pode vir em formatos diferentes, como aaaa-mm-dd.
    """
    if 'dataNascimento' not in df.columns:
        return df

    datas_convertidas = pd.to_datetime(df['dataNascimento'], errors='coerce')
    df['dataNascimento'] = datas_convertidas.dt.strftime('%d/%m/%Y')
    return df

def carregar_dados(caminho_covid, caminho_mapa):
    """
    Carrega o dataset da COVID e o arquivo de mapeamento de municípios/regiões.
    Retorna os dois DataFrames gerados pelo pandas.
    """
    df_covid = pd.read_csv(caminho_covid, low_memory=False)
    df_mapa = pd.read_csv(caminho_mapa)
    df_covid = remover_colunas_indice(df_covid)
    df_mapa = remover_colunas_indice(df_mapa)
    return df_covid, df_mapa

def limpar_dataset(df_covid, df_mapa):
    """
    Realiza a limpeza do dataset conforme as regras estabelecidas:
    1. Remove registros com o atributo 'municipioCaso' ausente (nulo).
    2. Trata diferenças de caixa (maiúscula/minúscula) e espaços para evitar falsos negativos.
    3. Remove registros cujo município não tem correspondência no mapa de regiões.
    """
    # 1. Remove registros onde 'municipioCaso' é NaN ou nulo
    df_covid_limpo = df_covid.dropna(subset=['municipioCaso']).copy()
    
    # 2. Padroniza os nomes dos municípios em ambos os datasets
    # Criamos colunas temporárias ('_padronizado') para realizar a comparação correta
    df_covid_limpo['municipioCaso_padronizado'] = limpar_textos(df_covid_limpo['municipioCaso'])
    df_mapa['municipio_padronizado'] = limpar_textos(df_mapa['municipio'])
    
    # Criamos uma lista (ou set) de municípios válidos que estão no arquivo de mapa
    municipios_validos = set(df_mapa['municipio_padronizado'].unique())
    
    # 3. Mantém apenas os registros cujo município (padronizado) exista no conjunto de municípios do mapa
    df_covid_limpo = df_covid_limpo[df_covid_limpo['municipioCaso_padronizado'].isin(municipios_validos)]
    
    # Removemos a coluna temporária criada para a padronização, preservando a estrutura original
    df_covid_limpo = df_covid_limpo.drop(columns=['municipioCaso_padronizado'])
    df_covid_limpo = normalizar_data_nascimento(df_covid_limpo)
    
    return df_covid_limpo

def main():
    """
    Função principal que orquestra a leitura, o pré-processamento de limpeza e o salvamento dos dados.
    """
    arquivo_covid = os.path.join('dados', 'covid.csv')
    arquivo_mapa = os.path.join('dados', 'map_municipio_regiao.csv')
    arquivo_saida = 'covid_limpo.csv'
    
    try:
        print("Carregando datasets...")
        df_covid, df_mapa = carregar_dados(arquivo_covid, arquivo_mapa)
        
        print(f"Total de registros originais na base covid: {len(df_covid)}")
        
        df_limpo = limpar_dataset(df_covid, df_mapa)
        
        print(f"Total de registros válidos após limpeza: {len(df_limpo)}")
        
        print(f"Salvando o resultado no arquivo '{arquivo_saida}'...")
        # Salva o resultado sem incluir o índice das linhas gerado pelo pandas
        df_limpo.to_csv(arquivo_saida, index=False)
        print("Limpeza concluída com sucesso!")
        
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado. Detalhes: {e}")
        print(f"Certifique-se de que os arquivos '{arquivo_covid}' e '{arquivo_mapa}' existem.")
    except Exception as e:
        print(f"Ocorreu um erro durante a execução: {e}")

if __name__ == "__main__":
    main()
