# Trabalho 1 - Anonimização Sintática

Este projeto implementa uma solução de anonimização de dados baseada em técnicas de generalização sintática. O objetivo principal é proteger informações sensíveis de um conjunto de dados sobre COVID-19 (`covid.csv`), generalizando os atributos demográficos `municipioCaso` e `dataNascimento` através de diferentes níveis de hierarquia.

## Dados

- A base de COVID-19 (`covid.csv`) foi disponibilizada pelo professor da disciplina.
- São dados públicos.
- Ela **não está neste repositório**. Cada linha é um caso individual, com data de nascimento e município. Assim o repositório não redistribui esse tipo de registro.
- Para rodar, coloque estes dois arquivos na pasta `dados/`:
  - `dados/covid.csv`
  - `dados/map_municipio_regiao.csv` (mapa município → região de saúde)
- `covid_limpo.csv` e `DT_0_3.csv` também não estão aqui. Os scripts geram os dois.

## 📁 Estrutura de Pastas e Arquivos

O projeto está organizado da seguinte maneira:

- `dados/`
  - `covid.csv`: (fora do repositório) Base de dados original contendo os registros médicos e demográficos.
  - `map_municipio_regiao.csv`: (fora do repositório) Arquivo de mapeamento contendo a relação entre os municípios e suas respectivas Regiões de Saúde.
- `hierarquias/`: Diretório gerado automaticamente que armazena os dicionários JSON das hierarquias. O `data_hierarquia.json` não está no repositório (ele lista as datas de nascimento da base). O `gerar_hierarquias.py` cria o arquivo.
- `plots/`: Diretório gerado automaticamente para salvar os histogramas gerados (formato `.png`).
- `pre_processamento.py`: Script para limpeza e padronização dos dados originais.
- `gerar_hierarquias.py`: Script para montagem das árvores/dicionários de generalização.
- `anonimizacao.py`: Script principal interativo para a geração dos datasets anonimizados.
- `covid_limpo.csv`: (fora do repositório) Dataset gerado após a remoção dos registros sem mapeamento válido.
- `DT_0_3.csv`: (fora do repositório) Dataset de publicação gerado como exemplo, mantendo município no nível 0 e data no nível 3.
- `README.md`: Este arquivo com instruções do projeto.

## ⚙️ Decisões de Implementação

### 1. Limpeza de Dados
Foi definido que registros que não contenham informação de município, ou cujo município não esteja listado no mapeamento oficial (`map_municipio_regiao.csv`), devem ser completamente descartados do dataset para evitar anomalias geográficas. Todos os textos foram padronizados para letras maiúsculas e sem espaços adicionais.

### 2. Generalização de Municípios (3 Níveis)
- **Nível 0**: Município exato original.
- **Nível 1**: Região de saúde correspondente (baseada no arquivo de mapeamento).
- **Nível 2**: Estado fixado em "CEARA".

### 3. Generalização de Datas de Nascimento (4 Níveis) e a Faixa de 5 Anos
A especificação exigiu a criação de 4 níveis para `dataNascimento`, sendo:
- **Nível 0**: Data exata (dd/mm/aaaa)
- **Nível 1**: Mês e Ano (mm/aaaa)
- **Nível 2**: Ano (aaaa)
- **Nível 3**: Intervalo de 5 anos.

**Lógica do Intervalo de 5 Anos (Nível 3):**
Para agrupar os anos em faixas fixas, não sobrepostas (ex: 1991-1995, 1996-2000), adotou-se a seguinte fórmula matemática para extrair o ano de início de uma faixa:
```python
inicio_intervalo = ((ano - 1) // 5) * 5 + 1
```
*Explicação:* 
Subtraímos `1` do ano antes da divisão para tratar corretamente os anos terminados em 0 ou 5 (como 2000 ou 1995). Por exemplo, para o ano 2000: `((2000 - 1) // 5) * 5 + 1 = 1996`. Assim, o intervalo gerado é exatamente `1996-2000`. Essa abordagem evita laços excessivos, baseando-se estritamente em propriedades aritméticas.

## 🚀 Como Executar o Projeto

O projeto foi construído na linguagem Python e necessita das bibliotecas `pandas` e `matplotlib`.

Antes de executar, instale as dependências:

```bash
pip install -r requirements.txt
```

O processo deve ser executado em 3 etapas sequenciais:

### Etapa 1: Pré-processamento
Limpa a base de dados original e alinha os municípios.
```bash
python pre_processamento.py
```
*(Será gerado o arquivo `covid_limpo.csv` na pasta raiz).*

### Etapa 2: Geração das Hierarquias
Gera os arquivos `.json` com o dicionário de generalização de cada atributo.
```bash
python gerar_hierarquias.py
```
*(Serão gerados `municipio_hierarquia.json` e `data_hierarquia.json` na pasta `hierarquias/`).*

### Etapa 3: Execução Interativa e Geração de Datasets
Rode o script principal para interagir com o programa.
```bash
python anonimizacao.py
```
- O script criará inicialmente os gráficos originais de Nível 0 na pasta `plots/`.
- Informe os níveis numéricos desejados para Município (`nm` de 0 a 2) e Data de Nascimento (`nd` de 0 a 3).
- O dataset generalizado será gerado como `DT_{nm}_{nd}.csv`.
- Os respectivos histogramas de frequência dos dados generalizados serão salvos em `plots/`.
- Digite `-1` para ambos os atributos para encerrar o laço e o programa.

Exemplo:
```bash
nm = 0
nd = 3
```
Esse exemplo gera `DT_0_3.csv`, mantendo o município original e trocando `dataNascimento` por faixas de 5 anos.

---

Desenvolvido por Isaack Nyllo e Antônio Leite para a disciplina de Privacidade de Dados. Organização do repositório com apoio de IA.
