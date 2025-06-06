import requests
import pandas as pd
import sqlite3

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
        df.columns = ['open', 'high', 'low', 'close', 'volume']

        # Adicionando a coluna DateTime como string
        df.insert(0, 'datetime', df.index.astype(str))

        # Convertendo as colunas numéricas para float
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

        return df

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição à API: {e}")
    except ValueError as e:
        print(f"Erro nos dados: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

    return None  # Retorna None em caso de erro

import sqlite3
def get_or_insert_symbol(symbol):
    """
    Insere o symbol na tabela tbtitulos se não existir e retorna o id_titulos correspondente.

    Parâmetros:
    - symbol (str): Símbolo a ser verificado/inserido.

    Retorna:
    - id_titulos (int): ID correspondente ao símbolo inserido ou já existente.
    """
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect('sqtitulosalpha.db')
        cursor = conn.cursor()

        # Verificar se o símbolo já existe
        cursor.execute("SELECT id_titulos FROM tbtitulos WHERE symbol = ?", (symbol,))
        result = cursor.fetchone()

        if result:
            id_titulos = result[0]  # Retorna o ID já existente
        else:
            # Inserir o novo símbolo
            cursor.execute("INSERT INTO tbtitulos (symbol) VALUES (?)", (symbol,))
            conn.commit()

            # Obter o ID do símbolo recém-inserido
            id_titulos = cursor.lastrowid

        # Fechar a conexão
        conn.close()

        return id_titulos

    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
        return None


import sqlite3

def get_or_insert_interval(interval):
    """
    Insere o intervalo intraiario na tabela tbintervalos se não existir e retorna o id_intervalos correspondente.

    Parâmetros:
    - interval (str): Intervalo a ser verificado/inserido.

    Retorna:
    - id_intervalos (int): ID correspondente ao intervalo inserido ou já existente.
    """
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect('sqtitulosalpha.db')
        cursor = conn.cursor()

        # Verificar se o intervalo já existe
        cursor.execute("SELECT id_intervalos FROM tbintervalos WHERE intervalo = ?", (interval,))
        result = cursor.fetchone()

        if result:
            id_intervalos = result[0]  # Retorna o ID já existente
        else:
            # Inserir o novo intervalo
            cursor.execute("INSERT INTO tbintervalos (intervalo) VALUES (?)", (interval,))
            conn.commit()

            # Obter o ID do intervalo recém-inserido
            id_intervalos = cursor.lastrowid

        # Fechar a conexão
        conn.close()

        return id_intervalos

    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
        return None


import sqlite3

def get_or_insert_titulos_intervalos(id_titulos, id_intervalos):
    """
    Insere a combinação id_titulos e id_intervalos na tabela tbtitulosintervalos se não existir 
    e retorna o id_titulosintervalos correspondente.

    Parâmetros:
    - id_titulos (int): ID do título.
    - id_intervalos (int): ID do intervalo.

    Retorna:
    - id_titulosintervalos (int): ID correspondente ao registro inserido ou já existente.
    """
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect('sqtitulosalpha.db')
        cursor = conn.cursor()

        # Verificar se já existe um registro com esses valores
        cursor.execute("""
            SELECT id_titulosintervalos FROM tbtitulosintervalos 
            WHERE id_titulos = ? AND id_intervalos = ?
        """, (id_titulos, id_intervalos))
        result = cursor.fetchone()

        if result:
            id_titulosintervalos = result[0]  # Retorna o ID já existente
        else:
            # Inserir novo registro
            cursor.execute("""
                INSERT INTO tbtitulosintervalos (id_titulos, id_intervalos) 
                VALUES (?, ?)
            """, (id_titulos, id_intervalos))
            conn.commit()

            # Obter o ID do novo registro inserido
            id_titulosintervalos = cursor.lastrowid

        # Fechar conexão
        conn.close()

        return id_titulosintervalos

    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
        return None


import sqlite3

def insert_titulos_prezos(id_titulosintervalos, df):
    """
    Insere registros do dataframe df na tabela tbtitulosprezos se não existirem.

    Parâmetros:
    - id_titulosintervalos (int): ID do título-intervalo.
    - df (DataFrame): DataFrame contendo colunas datetime, open, high, low, close, volume.

    Retorna:
    - Quantidade de registros inseridos.
    """
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect('sqtitulosalpha.db')
        cursor = conn.cursor()

        # Iterar sobre o dataframe e inserir dados que não existam
        inserted_count = 0
        for _, row in df.iterrows():
            cursor.execute("""
                SELECT COUNT(*) FROM tbtitulosprezos 
                WHERE id_titulosintervalos = ? AND datetime = ?
            """, (id_titulosintervalos, row['datetime']))
            exists = cursor.fetchone()[0]

            if not exists:
                cursor.execute("""
                    INSERT INTO tbtitulosprezos (id_titulosintervalos, datetime, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (id_titulosintervalos, row['datetime'], row['open'], row['high'], row['low'], row['close'], row['volume']))
                inserted_count += 1

        conn.commit()
        conn.close()

        return inserted_count

    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
        return None