
def fore_import (dftitulos,id_especifico) :
    import sqlite3
    import pandas as pd
    
    # defino a url para fazer scrap e as variaveis para o processo
    
    dftituloselec = dftitulos[dftitulos["id_titulos"] == id_especifico]
    dftituloselec.columns = dftituloselec.columns.str.strip()  # Remove espaços nos nomes das colunas
    # Definir a url 
    url=(dftituloselec['url'].iloc[0]) #define a url para a função get_fore_dados(url)
    symbol= str(dftituloselec['symbol'].iloc[0])
    id_titulos= int(dftituloselec['id_titulos'].iloc[0])
    
    # chamo a la função que face scrap
    
    from forefunc import get_fore_dados 
    # Chamar a função para obter os dados de scrap
    df_forecasts_scrap, last_updated = get_fore_dados(url)
    
    #Insere os dados de scrap na tbforecasts

    import importlib
    import forefunc
    importlib.reload(forefunc)
    from forefunc  import insere_forecast
    id_forecastins, existsforecast = insere_forecast(id_titulos,last_updated)

    #Crea o df para inserir dados na tabela tbforecasthist
    
    # Valores do DataFrame original
    primeiro_date = str(df_forecasts_scrap["Date"].iloc[0])  # Pegando o primeiro valor de Date
    primeiro_forecast_value = float(df_forecasts_scrap["Forecast Value"].iloc[0])  # Pegando o primeiro valor de Forecast Value
    # Criando o novo DataFrame
    dftituloshistins = pd.DataFrame({
    "id_titulos": [id_titulos],
    "data": [primeiro_date],
    "valor": [primeiro_forecast_value]
    })

    #Insere registro na tbforecasthist    
    import importlib
    import forefunc
    importlib.reload(forefunc)
    from forefunc import forecasthist_insere    
    existshist = forecasthist_insere(dftituloshistins)

    #Crea os registros para inserir na tabela tbforecastsdados    
    dfforecastsdados = pd.DataFrame({    
    "id_forecasts":  [int(id_forecastins)] * len(df_forecasts_scrap),
    "data": df_forecasts_scrap['Date'], 
    "valor": df_forecasts_scrap['Forecast Value'],
    "error": df_forecasts_scrap['Avg Error'] ,
    })
    
    # Insere registros na tabela tbforecastsdados
    import importlib
    import forefunc
    importlib.reload(forefunc)
    from forefunc import forecastsdados_insere
    existsforecastsdados = forecastsdados_insere (dfforecastsdados)

    #Crea uma lista com os mensagens a enviar
    if existsforecast == 0:
        msj = f'O forecast do título {symbol} do forecast updated {last_updated} se atualizou corretamente\n existshist= {existshist}\n existsforecastsdados= {existsforecastsdados} '
    elif existsforecast == 1:
        msj = f'O forecast do título {symbol} do forecast updated {last_updated} já existe \n existshist= {existshist}\n existsforecastsdados= {existsforecastsdados}'
    return msj






    