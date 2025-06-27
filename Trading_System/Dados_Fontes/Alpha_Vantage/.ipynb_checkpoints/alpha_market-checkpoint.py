import requests
import pandas as pd

def alpha_market_data_intra(function, symbol, interval, month, apikey):
    """
    Função para buscar dados de mercado da API Alpha Vantage.

    Parâmetros:
    - function: Função da API (exemplo: TIME_SERIES_INTRADAY).
    - symbol: Símbolo do ativo (exemplo: GGAL).
    - interval: Intervalo de tempo (exemplo: 60min).
    - month: Mês específico para dados históricos (exemplo: 2009-02).
    - apikey: Chave de acesso à API.

    Retorna:
    - Um dataframe pandas com os dados formatados ou None em caso de erro.
    """
    try:
        # Construindo a URL dinamicamente
        url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&month={month}&outputsize=full&apikey={apikey}'
        r = requests.get(url)
        r.raise_for_status()  # Verifica se houve erro na requisição HTTP

        # Convertendo a resposta para JSON
        data = r.json()
        
        # Extraindo os dados do JSON
        time_series = data.get(f'Time Series ({interval})', {})

        if not time_series:
            raise ValueError("Nenhum dado encontrado para os parâmetros fornecidos.")

        # Convertendo para um dataframe do pandas
        df = pd.DataFrame.from_dict(time_series, orient='index')

        # Renomeando colunas para algo mais intuitivo
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        # Adicionando a coluna DateTime como string
        df.insert(0, 'DateTime', df.index.astype(str))

        # Convertendo as colunas numéricas para float
        df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)

        return df

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição à API: {e}")
    except ValueError as e:
        print(f"Erro nos dados: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

    return None  # Retorna None em caso de erro

# Exemplo de uso:
df = alpha_market_data_intra(function, symbol, interval, month, apikey)
display(df)
%%writefile alpha_market.py
