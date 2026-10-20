import pandas as pd
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def carregar_hierarquias():
    """Carrega os arquivos JSON com as hierarquias de generalização."""
    caminho_mun = os.path.join('hierarquias', 'municipio_hierarquia.json')
    caminho_data = os.path.join('hierarquias', 'data_hierarquia.json')
    
    with open(caminho_mun, 'r', encoding='utf-8') as f:
        hierarquia_municipio = json.load(f)
        
    with open(caminho_data, 'r', encoding='utf-8') as f:
        hierarquia_data = json.load(f)
        
    return hierarquia_municipio, hierarquia_data

def anonimizar_dataset(df, hierarquia_mun, hierarquia_data, nm, nd):
    """
    Substitui os valores originais do dataset pelos valores da hierarquia no nível especificado.
    Retorna uma cópia do dataframe com as substituições.
    """
    df_anonimizado = df.copy()
    
    nivel_mun = f"nivel {nm}"
    nivel_data = f"nivel {nd}"
    
    if nivel_mun not in hierarquia_mun:
        print(f"Erro: {nivel_mun} não existe na hierarquia de município.")
        return None
    if nivel_data not in hierarquia_data:
        print(f"Erro: {nivel_data} não existe na hierarquia de data.")
        return None
        
    # Mapeia os valores atuais utilizando o dicionário gerado
    # Importante converter para string pois as chaves do JSON são strings
    df_anonimizado['municipioCaso'] = df_anonimizado['municipioCaso'].astype(str).map(hierarquia_mun[nivel_mun])
    df_anonimizado['dataNascimento'] = df_anonimizado['dataNascimento'].astype(str).map(hierarquia_data[nivel_data])

    if df_anonimizado['municipioCaso'].isna().any():
        print("Erro: existem municípios sem correspondência na hierarquia.")
        return None

    datas_originais_preenchidas = df['dataNascimento'].notna()
    if df_anonimizado.loc[datas_originais_preenchidas, 'dataNascimento'].isna().any():
        print("Erro: existem datas de nascimento sem correspondência na hierarquia.")
        return None
    
    return df_anonimizado

def gerar_histograma(df, coluna, nivel, esconder_x=False):
    """
    Gera um histograma de frequências para uma coluna e o salva na pasta 'plots/'.
    """
    if not os.path.exists('plots'):
        os.makedirs('plots')
        
    print(f"Gerando histograma de {coluna} no nível {nivel}...")
    plt.figure(figsize=(10, 6))
    
    if coluna == 'dataNascimento':
        contagem = df[coluna].value_counts()
        
        if nivel == 0:
            idx = pd.to_datetime(contagem.index, dayfirst=True, errors='coerce')
            contagem = contagem.iloc[idx.argsort()]
        elif nivel == 1:
            idx = pd.to_datetime(contagem.index, format='%m/%Y', errors='coerce')
            contagem = contagem.iloc[idx.argsort()]
        else:
            contagem = contagem.sort_index()
            
        ax = contagem.plot(kind='bar')
        
        step = max(1, len(contagem) // 15)
        ticks = ax.xaxis.get_ticklocs()
        ticklabels = [l.get_text() for l in ax.xaxis.get_ticklabels()]
        
        ax.xaxis.set_ticks(ticks[::step])
        ax.xaxis.set_ticklabels(ticklabels[::step], rotation=45, ha='right')
        plt.xlabel(coluna)
        
    else:
        contagem = df[coluna].value_counts().sort_values(ascending=False)
        
        if not esconder_x and len(contagem) > 60:
            esconder_x = True
            
        if esconder_x:
            plt.bar(range(len(contagem)), contagem.values)
            plt.xticks([])
            plt.xlabel(f'{coluna} (rótulos ocultos)')
        else:
            plt.bar(contagem.index.astype(str), contagem.values)
            plt.xticks(rotation=45, ha='right')
            plt.xlabel(coluna)
        
    plt.title(f'Frequência de {coluna} (Nível {nivel})')
    plt.ylabel('Frequência')
        
    plt.tight_layout()
    nome_arquivo = os.path.join('plots', f'HIST_{coluna}_{nivel}.png')
    plt.savefig(nome_arquivo)
    plt.close()

def analise_sexo_resultado(df, nm, nd):
    if 'sexoCaso' in df.columns and 'resultadoFinalExame' in df.columns:
        plt.figure(figsize=(10, 6))
        cross_tab = pd.crosstab(df['sexoCaso'], df['resultadoFinalExame'])
        cross_tab.plot(kind='bar', stacked=True, ax=plt.gca())
        plt.title('Distribuição de Casos por Sexo e Resultado')
        plt.xlabel('Sexo')
        plt.ylabel('Frequência')
        plt.tight_layout()
        plt.savefig(os.path.join('plots', f'ANALISE_Sexo_Resultado_nm{nm}_nd{nd}.png'))
        plt.close()

def analise_positivos_municipio(df, nm, nd):
    if 'municipioCaso' in df.columns and 'resultadoFinalExame' in df.columns:
        plt.figure(figsize=(10, 6))
        positivos = df[df['resultadoFinalExame'].astype(str).str.upper() == 'POSITIVO']
        contagem = positivos['municipioCaso'].value_counts().sort_values(ascending=False).head(20)
        contagem.plot(kind='bar', ax=plt.gca())
        plt.title(f'Top 20 - Casos Positivos por Município (nm={nm})')
        plt.ylabel('Casos Positivos')
        if nm == 0:
            plt.xticks([])
            plt.xlabel('Município (rótulos ocultos)')
        else:
            plt.xticks(rotation=45, ha='right')
            plt.xlabel('Município/Região/Estado')
        plt.tight_layout()
        plt.savefig(os.path.join('plots', f'ANALISE_Positivos_Mun_nm{nm}_nd{nd}.png'))
        plt.close()

def analise_comorbidades(df, nm, nd):
    comorbidades = [c for c in df.columns if c.startswith('comorbidade')]
    if comorbidades:
        plt.figure(figsize=(10, 6))
        contagem = {}
        for c in comorbidades:
            quant = df[df[c].astype(str).str.upper().isin(['1', '1.0', 'SIM'])].shape[0]
            nome_limpo = c.replace('comorbidade', '').replace('Sivep', '')
            contagem[nome_limpo] = quant
            
        serie = pd.Series(contagem).sort_values(ascending=True)
        serie.tail(10).plot(kind='barh', ax=plt.gca())
        plt.title('Top 10 Comorbidades mais Frequentes')
        plt.xlabel('Quantidade')
        plt.tight_layout()
        plt.savefig(os.path.join('plots', f'ANALISE_Comorbidades_nm{nm}_nd{nd}.png'))
        plt.close()

def main():
    arquivo_covid = 'covid_limpo.csv'
    
    # Verifica se os arquivos necessários existem
    if not os.path.exists(arquivo_covid):
        print(f"Erro: '{arquivo_covid}' não encontrado. Rode o pre_processamento.py primeiro.")
        return
        
    if not os.path.exists('hierarquias'):
        print("Erro: A pasta 'hierarquias' não existe. Rode gerar_hierarquias.py primeiro.")
        return

    print("Carregando base de dados... (isso pode levar alguns segundos)")
    df_covid = pd.read_csv(arquivo_covid, low_memory=False)
    df_covid = df_covid.drop(columns=[c for c in df_covid.columns if c.startswith('Unnamed:')], errors='ignore')
    
    print("Carregando hierarquias...")
    hierarquia_mun, hierarquia_data = carregar_hierarquias()
    
    print("Gerando histogramas originais (Nível 0)...")
    gerar_histograma(df_covid, 'municipioCaso', 0, esconder_x=True)
    gerar_histograma(df_covid, 'dataNascimento', 0, esconder_x=False)
    
    print("Gerando análises avançadas originais (Nível 0)...")
    analise_sexo_resultado(df_covid, 0, 0)
    analise_positivos_municipio(df_covid, 0, 0)
    analise_comorbidades(df_covid, 0, 0)
    
    while True:
        try:
            print("\n" + "="*50)
            entrada_nm = input("Digite o nível de generalização do município (nm: 0, 1, 2) [ou -1 para sair]: ").strip()
            
            if entrada_nm == '-1':
                print("Encerrando o programa...")
                break
                
            entrada_nd = input("Digite o nível de generalização da data (nd: 0, 1, 2, 3) [ou -1 para sair]: ").strip()
            
            if entrada_nd == '-1':
                print("Encerrando o programa...")
                break
            
            nm = int(entrada_nm)
            nd = int(entrada_nd)
            
            if nm not in [0, 1, 2]:
                print("Nível de município (nm) inválido. Escolha 0, 1 ou 2.")
                continue
                
            if nd not in [0, 1, 2, 3]:
                print("Nível de data (nd) inválido. Escolha 0, 1, 2 ou 3.")
                continue
                
            print(f"\nGerando dataset de publicação para nm={nm} e nd={nd}...")
            df_novo = anonimizar_dataset(df_covid, hierarquia_mun, hierarquia_data, nm, nd)
            
            if df_novo is not None:
                nome_saida = f"DT_{nm}_{nd}.csv"
                df_novo.to_csv(nome_saida, index=False)
                print(f"Dataset salvo com sucesso: {nome_saida} ({len(df_novo)} registros originais mantidos).")
                
                print("Gerando histogramas para os dados generalizados (aguarde...).")
                gerar_histograma(df_novo, 'municipioCaso', nm, esconder_x=(nm == 0))
                gerar_histograma(df_novo, 'dataNascimento', nd, esconder_x=False)
                
                print("Gerando análises: Distribuição por Sexo...")
                analise_sexo_resultado(df_novo, nm, nd)
                
                print("Gerando análises: Casos Positivos por Município...")
                analise_positivos_municipio(df_novo, nm, nd)
                
                print("Gerando análises: Comorbidades Principais...")
                analise_comorbidades(df_novo, nm, nd)
                
                print("-> Todos os gráficos foram gerados com sucesso na pasta 'plots/'!")
                
        except ValueError:
            print("Entrada inválida! Por favor, digite apenas números inteiros válidos.")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()
