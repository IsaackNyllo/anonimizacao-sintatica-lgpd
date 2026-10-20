import pandas as pd
import json
import os

def limpar_texto(valor):
    """Padroniza textos usados como chave de comparação."""
    return str(valor).strip().upper()

def gerar_hierarquia_municipio(df_covid, df_mapa):
    """
    Gera a hierarquia de 3 níveis para o atributo 'municipioCaso'.
    Nível 0: Dado original (município)
    Nível 1: Região de saúde correspondente
    Nível 2: Estado (sempre 'Ceará')
    """
    hierarquia = {
        "nivel 0": {},
        "nivel 1": {},
        "nivel 2": {}
    }
    
    # Criar um dicionário de busca rápida para mapear município -> região
    # Convertendo para maiúsculas e removendo espaços para garantir o acerto
    mapa_dict = {}
    for _, row in df_mapa.iterrows():
        mun_padronizado = limpar_texto(row['municipio'])
        regiao = str(row['regiao']).strip().upper()
        mapa_dict[mun_padronizado] = regiao
        
    # Extrai os municípios únicos do dataset limpo
    municipios_unicos = df_covid['municipioCaso'].dropna().unique()
    
    for mun in municipios_unicos:
        # A chave deve ser exatamente o dado original para facilitar o mapeamento posterior
        # Para buscar a região, padronizamos da mesma forma que fizemos antes
        mun_busca = limpar_texto(mun)
        
        if mun_busca not in mapa_dict:
            continue

        regiao = mapa_dict[mun_busca]
        
        hierarquia["nivel 0"][mun] = mun
        hierarquia["nivel 1"][mun] = regiao
        hierarquia["nivel 2"][mun] = "CEARA"
        
    return hierarquia

def gerar_hierarquia_data(df_covid):
    """
    Gera a hierarquia de 4 níveis para o atributo 'dataNascimento'.
    Nível 0: Dado original (dd/mm/aaaa)
    Nível 1: Ano e mês (mm/aaaa)
    Nível 2: Apenas o ano (aaaa)
    Nível 3: Intervalos de 5 anos (ex.: 1991–1995)
    """
    hierarquia = {
        "nivel 0": {},
        "nivel 1": {},
        "nivel 2": {},
        "nivel 3": {}
    }
    
    datas_unicas = df_covid['dataNascimento'].dropna().unique()
    
    for data in datas_unicas:
        # Pega a string exata do arquivo como chave
        data_str = str(data).strip()
        
        data_convertida = pd.to_datetime(data_str, dayfirst=True, errors='coerce')
        
        if not pd.isna(data_convertida):
            data_nivel_0 = data_convertida.strftime('%d/%m/%Y')
            mes_ano = data_convertida.strftime('%m/%Y')
            ano = int(data_convertida.year)

            # Cálculo do intervalo de 5 anos
            # Exemplo: (1993 - 1) // 5 = 398. 398 * 5 + 1 = 1991. (1991 a 1995)
            # Para anos como 2000: (2000 - 1) // 5 = 399. 399 * 5 + 1 = 1996. (1996 a 2000)
            inicio_intervalo = ((ano - 1) // 5) * 5 + 1
            fim_intervalo = inicio_intervalo + 4
            intervalo_str = f"{inicio_intervalo}-{fim_intervalo}"
            
            hierarquia["nivel 0"][data_str] = data_nivel_0
            hierarquia["nivel 1"][data_str] = mes_ano
            hierarquia["nivel 2"][data_str] = str(ano)
            hierarquia["nivel 3"][data_str] = intervalo_str
        else:
            # Caso a data não possa ser interpretada, mantém o valor original
            hierarquia["nivel 0"][data_str] = data_str
            hierarquia["nivel 1"][data_str] = data_str
            hierarquia["nivel 2"][data_str] = data_str
            hierarquia["nivel 3"][data_str] = data_str
            
    return hierarquia

def main():
    arquivo_covid = 'covid_limpo.csv'
    arquivo_mapa = os.path.join('dados', 'map_municipio_regiao.csv')
    
    dir_saida = 'hierarquias'
    # Cria o diretório se não existir
    if not os.path.exists(dir_saida):
        os.makedirs(dir_saida)
        print(f"Diretório '{dir_saida}' criado com sucesso.")
        
    try:
        print("Carregando datasets...")
        df_covid = pd.read_csv(arquivo_covid, low_memory=False)
        df_mapa = pd.read_csv(arquivo_mapa)
        df_covid = df_covid.drop(columns=[c for c in df_covid.columns if c.startswith('Unnamed:')], errors='ignore')
        df_mapa = df_mapa.drop(columns=[c for c in df_mapa.columns if c.startswith('Unnamed:')], errors='ignore')
        
        print("Gerando hierarquia para 'municipioCaso'...")
        hierarquia_municipio = gerar_hierarquia_municipio(df_covid, df_mapa)
        
        print("Gerando hierarquia para 'dataNascimento'...")
        hierarquia_data = gerar_hierarquia_data(df_covid)
        
        caminho_mun = os.path.join(dir_saida, 'municipio_hierarquia.json')
        caminho_data = os.path.join(dir_saida, 'data_hierarquia.json')
        
        # Salva em formato JSON, garantindo os caracteres com acentos (ensure_ascii=False)
        print(f"Salvando json em '{caminho_mun}'...")
        with open(caminho_mun, 'w', encoding='utf-8') as f:
            json.dump(hierarquia_municipio, f, ensure_ascii=False, indent=4)
            
        print(f"Salvando json em '{caminho_data}'...")
        with open(caminho_data, 'w', encoding='utf-8') as f:
            json.dump(hierarquia_data, f, ensure_ascii=False, indent=4)
            
        print("Hierarquias geradas e salvas com sucesso!")
        
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado - {e.filename}")
        print("Certifique-se de rodar o pré-processamento primeiro para gerar o 'covid_limpo.csv'.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()
