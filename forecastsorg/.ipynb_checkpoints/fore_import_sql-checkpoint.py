
# Função para obter os dados do índice
def get_fore_dados(url):
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup
    # Fazer a requisição HTTP para a página
    response = requests.get(url)
    response.raise_for_status()  # Verifica se houve erro na requisição

    # Criar o objeto BeautifulSoup para processar o HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Localizar a tabela pelo ID (caso tenha um identificador)
    table = soup.find("table", {"id": "forecast"})

    # Extrair todas as linhas da tabela
    rows = table.find_all("tr")[1:]  # Ignora o cabeçalho

    # Criar lista para armazenar os dados extraídos
    data_list = []

    for row in rows:
        cols = row.find_all("td")
        month = cols[1].text.strip()
        date = pd.to_datetime(month)  # Convertendo a string para uma data válida
        forecast_value = float(cols[2].text.strip())
        avg_error = float(cols[3].text.replace("±", "").strip())

        data_list.append([month, date, forecast_value, avg_error])

    # Criar DataFrame
    df_forecasts_scrap = pd.DataFrame(data_list, columns=["Month", "Date", "Forecast Value", "Avg Error"])

    # --- Capturar a data de atualização ---
    updated_text = soup.find("time").text.strip()
    updated_date = pd.to_datetime(updated_text.replace("Updated: ", ""))  # Converter para formato datetime

    return df_forecasts_scrap, updated_date

# Insere na tbforecasts um novo registro
def insere_forecast(id_titulos, data) :
    import sqlite3
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect("sqforecasts.db")
    cursor = conn.cursor()

    # Verificar se o registro já existe
    cursor.execute("SELECT COUNT(*) FROM tbforecasts WHERE id_titulos = ? AND data = ?", (id_titulos, str(data)))
    existsforecast = cursor.fetchone()[0]

    # Se não existir, inserir o novo registro
    if existsforecast == 0:
        cursor.execute("INSERT INTO tbforecasts (id_titulos, data) VALUES (?, ?)", (id_titulos, str(data)))
        conn.commit()

        # Valor do id do registro inserido
        id_forecastins = cursor.lastrowid
    else:
        id_forecastins = 0
    # Fechar conexão
    conn.close()
    return id_forecastins, existsforecast

# Insere um novo rrgistro na tabela tbtituloshist
def forecasthist_insere (dftituloshistins):
    import sqlite3
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect("sqforecasts.db")
    cursor = conn.cursor()
    
    # Definir os valores
    id_titulos = (dftituloshistins["id_titulos"].iloc[0]) 
    data = (dftituloshistins["data"].iloc[0]) 
    valor = (dftituloshistins["valor"].iloc[0]) 
    
    # Verificar se o registro já existe
    cursor.execute("SELECT COUNT(*) FROM tbtituloshist WHERE id_titulos = ? AND data = ?", (id_titulos, data))
    existshist = cursor.fetchone()[0]
    
    # Se não existir, inserir o novo registro
    if existshist == 0:
        cursor.execute("INSERT INTO tbtituloshist (id_titulos, data, valor) VALUES (?, ?, ?)", (id_titulos, data, valor))
        conn.commit()
        
    else:
        existshist = 1
    # Fechar conexão
    conn.close()
    return existshist
    
# Insere registros na tabela tbforecastsdados
def forecastsdados_insere (dfforecastsdados):
    import sqlite3
    # Conectar ao banco de dados
    conn = sqlite3.connect('sqforecasts.db')
    cursor = conn.cursor()
    
    # Obter IDs existentes na tabela
    cursor.execute("SELECT DISTINCT id_forecasts FROM tbforecastsdados")
    ids_existentes = {row[0] for row in cursor.fetchall()}  # Converte para conjunto (set) para busca rápida
    
    # Filtrar o DataFrame: manter apenas registros cujo id_forecasts não está na tabela
    dfforecastsdados_filtrado = dfforecastsdados[~dfforecastsdados['id_forecasts'].isin(ids_existentes)]
    
    # Verificar se há dados para inserir
    if not dfforecastsdados_filtrado.empty:
        # Inserir os dados filtrados no SQLite
        dfforecastsdados_filtrado.to_sql('tbforecastsdados', conn, if_exists='append', index=False)
        existsforecastsdados = 0
    else:
        existsforecastsdados = 1          
    # Fechar a conexão com o banco
    conn.close()
    return existsforecastsdados