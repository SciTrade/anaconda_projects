from decimal import Decimal
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import pyodbc
import json


serverName = '10.10.2.76\SQLEXPRESS,1433'
User = 'LoginPCMain'
Pass = 'datosentorno'
connectionString = 'Driver={ODBC Driver 17 for SQL Server};Server=' + serverName + ';Database=entorno;UID=' + User + ';PWD=' + Pass + ';'


def connect_to_database():
    # Realizar la consulta a la base de datos utilizando pyodbc
    conn = pyodbc.connect(connectionString)
    cursor = conn.cursor()
    return cursor

def execute_query(especie, query=None):
    cursor = connect_to_database()
    if(especie.endswith('REM')):
        cursor.execute(f"""SELECT * FROM datos 
                                WHERE especie LIKE '{ especie }0123' 
                                {query if query else ''} 
                                ORDER BY time ASC""")
    else:
        cursor.execute(f"SELECT * FROM datos WHERE especie LIKE '{ especie }%' {query if query else ''} ORDER BY time ASC")
    results = cursor.fetchall()
    # Devolver los resultados en un formato adecuado, como JSON
    results = [tuple(row) for row in results]
    keys = ['especie', 'time', 'close', 'high', 'low', 'open', 'fuente', 'fechaDato', 'tipoDato']
    results = [dict(zip(keys, row)) for row in results]
    return results

def generate_index(results):
    df = pd.DataFrame(results)
    df.loc[0, 'indice'] = 1
    for i in range(1, len(df)):
        df.loc[i, 'indice'] = df.loc[i-1, 'indice'] * (1 + df.loc[i, 'var'])
    df['indice'] = (df['indice'] - 1) * 100
    df = df[['time', 'indice']]
    df.rename(columns={'indice': 'close'}, inplace=True)
    results = df.to_dict('records')
    return results

def generate_var(results, already_var=False):
    df = pd.DataFrame(results)
    if already_var:
        df.rename(columns={'close': 'var'}, inplace=True)
        df['var'] = df['var'] / 100
        return df.to_dict('records')       
    df.loc[0, 'var'] = 0
    for i in range(1, len(df)):
        df.loc[i, 'var'] = df.loc[i, 'close'] / df.loc[i-1, 'close'] - 1
    results = df.to_dict('records')
    return results

def generate_json(results, filename='data'):
    data_for_chart = format_data_for_chart(results)
    # Exportar json generado en un archivo .json
    with open(f'database_data/static/database_data/{filename}.json', 'w') as outfile:
        json.dump(data_for_chart, outfile, default=str)

def generate_json_with_open_high_low(results, filename='data'):
    resultsHigh = [dict((k, v) for k, v in d.items() if k != 'close') for d in results]
    for result in resultsHigh:
        result['close'] = result['high']
        del result['high']
    data_for_chart = format_data_for_chart(resultsHigh)
    with open(f'database_data/static/database_data/{filename}_high.json', 'w') as outfile:
        json.dump(data_for_chart, outfile, default=str)

    resultsLow = [dict((k, v) for k, v in d.items() if k != 'close') for d in results]
    for result in resultsLow:
        result['close'] = result['low']
        del result['low']
    data_for_chart = format_data_for_chart(resultsLow)
    with open(f'database_data/static/database_data/{filename}_low.json', 'w') as outfile:
        json.dump(data_for_chart, outfile, default=str)

    data_for_chart = format_data_for_chart(results)
    with open(f'database_data/static/database_data/{filename}.json', 'w') as outfile:
        json.dump(data_for_chart, outfile, default=str)

def generate_response(results):
    # Generar la respuesta HTTP
    response = HttpResponse(json.dumps(results, indent=4, default=str), content_type="application/json")
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

def format_data_for_chart(results):
    # Exportar en un json con el formato de "time" y "value" para que funcione con el gráfico de TradingView
    data_for_chart = []
    for result in results:
        data_for_chart.append({
            "time": {
                "day": result['time'].day,
                "month": result['time'].month,
                "year": result['time'].year,
            }, 
            "value": round(result['close'], 1) 
        })
    #  Obtener los últimos 130 datos
    # data_for_chart = data_for_chart[-130:]
    return data_for_chart

def dolar_mep(request):
    if request.method == 'GET':
        results = execute_query('DOLARMEP')
        generate_json(results, 'dolar_mep')
        return generate_response(results)

def dolar_oficial(request):
    if request.method == 'GET':
        results = execute_query('DOLAROFICIAL')
        generate_json(results, 'dolar_oficial')
        return generate_response(results)

def dolar_blue(request):
    if request.method == 'GET':
        results = execute_query('DOLARBLUE')
        generate_json(results, 'dolar_blue')
        return generate_response(results)

def dolar_blue_weekly(request):
    if request.method == 'GET':
        results = execute_query('DOLARBLUE')
        results = results[::5]
        generate_json(results, 'dolar_blue_weekly')
        return generate_response(results)

def dolar_blue_monthly(request):
    if request.method == 'GET':
        results = execute_query('DOLARBLUE')
        results = results[::20]
        generate_json(results, 'dolar_blue_monthly')
        return generate_response(results)

def riesgo_pais(request):
    if request.method == 'GET':
        results = execute_query('RIESGOP')
        generate_json(results, 'riesgo_pais')
        return generate_response(results)

def ipc_usa(request):
    if request.method == 'GET':
        results = execute_query('IPCUSA')
        return generate_response(results)

def ipc_rem(request):
    if request.method == 'GET':
        results = execute_query('IPC_REM', """AND [tipo-dato] LIKE 'Var_mensual' 
                                AND [time]>='2023-01-31 00:00:00' 
                                AND [time]<='2024-01-31 23:59:59'""")
        generate_json(results, 'ipc_rem')
        return generate_response(results)

def ipc_rem_index(request):
    if request.method == 'GET':
        results = execute_query('IPC_REM', """AND [tipo-dato] LIKE 'Var_mensual' 
                                AND [time]>='2023-01-31 00:00:00' 
                                AND [time]<='2024-01-31 23:59:59'""")
        results = generate_var(results, already_var=True)
        results = generate_index(results)
        generate_json(results, 'ipc_rem_index')
        return generate_response(results)

def tcnpm_rem(request):
    if request.method == 'GET':
        results = execute_query('TCNPM_REM', "AND [time]>='2023-01-31 00:00:00' AND [time]<='2024-01-31 23:59:59'")
        generate_json(results, 'tcnpm_rem')
        return generate_response(results)

def tcnpm_rem_index(request):
    if request.method == 'GET':
        results = execute_query('TCNPM_REM', "AND [time]>='2023-01-31 00:00:00' AND [time]<='2024-01-31 23:59:59'")
        results = generate_var(results)
        results = generate_index(results)
        generate_json(results, 'tcnpm_rem_index')
        return generate_response(results)

def blue_rem(request):
    if request.method == 'GET':
        results = execute_query('BLUE_REM')
        generate_json_with_open_high_low(results, 'dolar_blue_rem')
        return generate_response(results)

def blue_rem_index(request):
    if request.method == 'GET':
        results = execute_query('BLUE_REM')
        results = generate_var(results)
        results = generate_index(results)
        generate_json(results, 'dolar_blue_rem_index')
        return generate_response(results)

def pibpc_rem(request):
    if request.method == 'GET':
        results = execute_query('PIBPC_REM')
        return generate_response(results)

def commod_fcast(request):
    if request.method == 'GET':
        results = execute_query('COMMOD_FCAST')
        return generate_response(results)

def dowj_fcast(request):
    if request.method == 'GET':
        results = execute_query('DOWJ_FCAST')
        return generate_response(results)

def dxy_fcast(request):
    if request.method == 'GET':
        results = execute_query('DXY_FCAST')
        return generate_response(results)

def eurusd_fcast(request):
    if request.method == 'GET':
        results = execute_query('EURUSD_FCAST')
        return generate_response(results)

def fedfund_fcast(request):
    if request.method == 'GET':
        results = execute_query('FEDFUND_FCAST')
        return generate_response(results)

def gold_fcast(request):
    if request.method == 'GET':
        results = execute_query('GOLD_FCAST')
        return generate_response(results)

def inflation_fcast(request):
    if request.method == 'GET':
        results = execute_query('INFLATION_FCAST')
        return generate_response(results)

def nasdaq_fcast(request):
    if request.method == 'GET':
        results = execute_query('NASDAQ_FCAST')
        return generate_response(results)

def oil_fcast(request):
    if request.method == 'GET':
        results = execute_query('OIL_FCAST')
        return generate_response(results)

def stpoor_fcast(request):
    if request.method == 'GET':
        results = execute_query('STPOOR_FCAST')
        return generate_response(results)

def us10y_fcast(request):
    if request.method == 'GET':
        results = execute_query('US10Y_FCAST')
        return generate_response(results)

def index(request):
    # Mensaje de presentación de la base de datos
    return HttpResponse("""
    <h1>Base de datos de datos de entorno</h1>
    <p>Esta base de datos contiene los datos de entorno</p>
    <p>Los datos disponibles son:</p>
    <ul>
        <li><a href="/mep">Dolar MEP</a></li>
        <li><a href="/oficial">Dolar Oficial</a></li>
        <li><a href="/blue">Dolar Blue</a></li>
        <li><a href="/blue-weekly">Dolar Blue Weekly</a></li>
        <li><a href="/blue-monthly">Dolar Blue Monthly</a></li>
        <li><a href="/riesgo-pais">Riesgo Pais</a></li>
        <li><a href="/ipc-usa">IPC USA</a></li>
        <li><a href="/rem/ipc">IPC REM</a></li>
        <li><a href="/rem/ipc-index">IPC REM Index</a></li>
        <li><a href="/rem/tcnpm">TCNPM REM</a></li>
        <li><a href="/rem/tcnpm-index">TCNPM REM Index</a></li>
        <li><a href="/rem/blue">Blue REM</a></li>
        <li><a href="/rem/blue-index">Blue REM Index</a></li>
        <li><a href="/rem/pibpc">PIBPC REM</a></li>
        <li><a href="/forecast/commod">Commodities Forecast</a></li>
        <li><a href="/forecast/dowj">Dow Jones Forecast</a></li>
        <li><a href="/forecast/dxy">DXY Forecast</a></li>
        <li><a href="/forecast/eurusd">EURUSD Forecast</a></li>
        <li><a href="/forecast/fedfund">Fed Fund Forecast</a></li>
        <li><a href="/forecast/gold">Gold Forecast</a></li>
        <li><a href="/forecast/inflation">Inflation Forecast</a></li>
        <li><a href="/forecast/nasdaq">NASDAQ Forecast</a></li>
        <li><a href="/forecast/oil">Oil Forecast</a></li>
        <li><a href="/forecast/stpoor">S&P 500 Forecast</a></li>
        <li><a href="/forecast/us10y">US 10Y Forecast</a></li>
    </ul>
    """)

