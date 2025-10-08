

from datetime import date, datetime
import sqlite3
import pandas as pd

            #conecta ao banco sqTradeSys  e exetrae os parametros gerales do back test da vista vwbacktest 

def backtest_parameters (id_backtest) : 
    import sqlite3
    import pandas as pd
    
    # Conecta ao banco de dados
    con = sqlite3.connect('sqTradeSys.db')  # ou o caminho correto do seu arquivo .sqlite
    
    # Consulta SQL para extrair o registro
    query = f"SELECT * FROM vwbacktest WHERE id_backtest = {id_backtest}"
    
    # Executa a consulta e lê em um DataFrame
    df = pd.read_sql_query(query, con)
    
    # Converte o primeiro (e único) registro em Series
    srbacktest = df.iloc[0] if not df.empty else None
    
    # Fecha a conexão (opcional)
    con.close()
    return srbacktest

                                #importa os dados historicos do Titulo a testar

import sqlite3
import pandas as pd

def titulos_dados (srbacktest) :
    # Caminho para o banco de dados
    caminho_bd =  srbacktest['source'] 
    # Conectando ao banco
    conexao = sqlite3.connect(caminho_bd)
    # Lendo a view
    #consulta = 'SELECT * FROM vwtitulosdados ORDER BY datetime'
    consulta = f"""
    SELECT * FROM vwtitulosdados
    WHERE datetime BETWEEN '{srbacktest['dataini']}' AND '{srbacktest['datafim']}' AND symbol = '{srbacktest['symbol']}' AND intervalo = '{srbacktest['intervalo']}' AND moeda = '{srbacktest['moeda']}'
    ORDER BY datetime
    """
    dftitulosdados = pd.read_sql_query(consulta, conexao)
    # Fechando a conexão
    conexao.close()
    dftitulosdados = dftitulosdados.drop(columns=["symbol", "moeda", "intervalo"])
    return dftitulosdados
    


                                #importa os parametros  e rangos dos scripts a executar
import sqlite3
import pandas as pd
                                
def scripts_parameters(id_backtest) :
    # Conecta ao banco de dados SQLite
    con = sqlite3.connect('sqTradeSys.db')  # ou o caminho correto do seu arquivo .sqlite
    
    # Consulta SQL para extrair o registro
    
    query = f"SELECT  name, type, max, min, step FROM vwbacktestparameters WHERE id_backtest = {id_backtest}"
    # Executa a consulta e lê em um DataFrame
    df = pd.read_sql_query(query, con)
    
    # Fecha a conexão (opcional)
    con.close()
    return df

                            #Gera um DataFrame com todas as combinações possíveis de parâmetros

import pandas as pd
import numpy as np
from itertools import product

def parameters_combinator(dfcomb: pd.DataFrame) -> pd.DataFrame:
    """
    Gera um DataFrame com todas as combinações possíveis de parâmetros
    definidos em dfcomb, respeitando os tipos especificados.

    Parâmetros esperados em dfcomb:
    - name: nome da coluna
    - type: tipo de dado ('int' ou 'float')
    - min: valor mínimo
    - max: valor máximo
    - step: incremento

    Retorna:
    - dfparamtest: DataFrame com todas as combinações possíveis
    """
    param_ranges = {}

    for _, row in dfcomb.iterrows():
        name = row['name']
        tipo = row['type']

        # Converte min, max, step para o tipo correto
        if tipo == 'int':
            min_val = int(row['min'])
            max_val = int(row['max'])
            step_val = int(row['step'])
        elif tipo == 'float':
            min_val = float(row['min'])
            max_val = float(row['max'])
            step_val = float(row['step'])
        else:
            raise ValueError(f"Tipo não suportado: {tipo}")

        # Gera a faixa de valores
        values = np.round(np.arange(min_val, max_val + step_val, step_val), 5)
        param_ranges[name] = values

    # Gera todas as combinações possíveis
    combinations = list(product(*param_ranges.values()))

    # Cria o novo DataFrame
    dfparamtest = pd.DataFrame(combinations, columns=param_ranges.keys())

    # Aplica os tipos definidos
    for _, row in dfcomb.iterrows():
        col = row['name']
        tipo = row['type']
        if tipo == 'int':
            dfparamtest[col] = dfparamtest[col].astype(int)
        elif tipo == 'float':
            dfparamtest[col] = dfparamtest[col].astype(float)

    return dfparamtest


                             #  Gera parametros e lista do almacenamento de metricas
import pandas as pd                 

def parametros (dfparamtest,il) :
    #Cria os parametros para os scripts     
    # System parameters
    # stoch_hml_1
    K = dfparamtest.loc[il,'K']
    D = dfparamtest.loc[il,'D']
    smoth = dfparamtest.loc[il,'smoth']
    medM = (dfparamtest.loc[il,'medM'])
    lowM = (dfparamtest.loc[il,'lowM'])
    
    # Backtesting parameters
    
    stpl = dfparamtest.loc[il,'stpl']
    comission = dfparamtest.loc[il,'comission']
    drawmax = dfparamtest.loc[il,'drawmax']

    #cria lista lsmetricas para almacenar as metricas
    # guarda na lista 
    lsmetricas = []
    srparamtest = dfparamtest.loc[il]
    lsmetricas.append(srparamtest)
    return K,D, smoth, medM, lowM, stpl, comission, drawmax, lsmetricas 



                        # gera um novo registro no df dfmetricas

def atualizar_df_metricas(dfmetricas, lsmetricas):
    """
    Adiciona uma linha ao DataFrame dfmetricas com os valores de lsmetricas.
    Se dfmetricas for None, cria o DataFrame com a estrutura das métricas.

    Parâmetros:
    - dfmetricas: pd.DataFrame ou None
    - lsmetricas: list de pd.Series

    Retorna:
    - pd.DataFrame atualizado
    """

    linha = pd.concat(lsmetricas)  # Une todas as Series em uma só

    if dfmetricas is None:
        # Cria o DataFrame com uma única linha
        dfmetricas = pd.DataFrame([linha.values], columns=linha.index)
    else:
        # Adiciona nova linha ao DataFrame existente
        dfmetricas.loc[len(dfmetricas)] = linha.values

    return dfmetricas




                                 # loop de processamento de parametros verção  simple

def processar_parametros_simple (dfparamtest, dftitulosdados, srbacktest, dfmetricas = None):
    
    from Stoch_HighMedLow_Long import Stoch_HighMedLow_Long
    from stoploss import stop_loss_reentry , stop_drawdown_simple
    from index import index_calculation
    from metrics import tir_total_anualizada , tir_anuais_df, tir_anuais_estats, trades_estats, drawdowns_df, drawdowns_estats, dias_out_df, dias_out_estats, stop_drawdown_df, stop_drawdown_estats 
    
    

    for indice, linha in dfparamtest.iterrows():    
        il = indice
        
        K,D, smoth, medM, lowM, stpl, comission, drawmax, lsmetricas =   parametros (dfparamtest, il)
        
        dfsignals = Stoch_HighMedLow_Long (dftitulosdados, K, D, smoth, medM , lowM)
        
        dfsignals, dfstoploss = stop_loss_reentry (dfsignals, stpl)
       
        dfindex = index_calculation (dfsignals, comission)
        
        dfindexdrawdown = stop_drawdown_simple(dfindex, drawmax)
        
        # METRICS
        # creo dataframe para calculo de metricas
        dfinputmetricas = dfindex[['datetime', 'state','index_sc', 'index','trade']]
        
        setirtotalanual , lsmetricas = tir_total_anualizada (dfinputmetricas, lsmetricas)
        
        dftiranual = tir_anuais_df (dfinputmetricas, srbacktest['dataini'], srbacktest['datafim'])
        setiranuaisestats , lsmetricas = tir_anuais_estats(dftiranual, lsmetricas)
        
        setradesestats, lsmetricas = trades_estats(dfinputmetricas, lsmetricas)
        
        dfdrawdowns = drawdowns_df(dfinputmetricas)
        sedrawdownsestats , lsmetricas = drawdowns_estats(dfdrawdowns, lsmetricas)
       
        dfdiasout = dias_out_df (dfinputmetricas)
        sediasoutestats, lsmetricas = dias_out_estats(dfdiasout, lsmetricas)
       
        dfstopdrawdown = stop_drawdown_df (dfindexdrawdown)
        sestopdrawdownestats, lsmetricas = stop_drawdown_estats(dfstopdrawdown, lsmetricas)
        #display (lsmetricas )
        dfmetricas = atualizar_df_metricas(dfmetricas, lsmetricas)
        
    return dfmetricas
                      


                                 # loop de processamento de parametros verção  multinúcleo

def processar_parametros_multinucleo(dfparamtest, dftitulosdados, srbacktest):
    
    from concurrent.futures import ThreadPoolExecutor
    import traceback  

    dfmetricas = None

    def processar_parametros(args):
        from Stoch_HighMedLow_Long import Stoch_HighMedLow_Long
        from stoploss import stop_loss_reentry , stop_drawdown_simple
        from index import index_calculation
        from metrics import tir_total_anualizada , tir_anuais_df, tir_anuais_estats, trades_estats, drawdowns_df, drawdowns_estats, dias_out_df, dias_out_estats, stop_drawdown_df, stop_drawdown_estats 

        
        il, linha, dftitulosdados, dataini, datafim = args
        try:
            K, D, smoth, medM, lowM, stpl, comission, drawmax, lsmetricas = parametros(dfparamtest, il)

            dfsignals = Stoch_HighMedLow_Long(dftitulosdados, K, D, smoth, medM, lowM)
            dfsignals, dfstoploss = stop_loss_reentry(dfsignals, stpl)
            dfindex = index_calculation(dfsignals, comission)
            dfindexdrawdown = stop_drawdown_simple(dfindex, drawmax)

            dfinputmetricas = dfindex[['datetime', 'state', 'index_sc', 'index', 'trade']]
            setirtotalanual, lsmetricas = tir_total_anualizada(dfinputmetricas, lsmetricas)
            dftiranual = tir_anuais_df(dfinputmetricas, dataini, datafim)
            setiranuaisestats, lsmetricas = tir_anuais_estats(dftiranual, lsmetricas)
            setradesestats, lsmetricas = trades_estats(dfinputmetricas, lsmetricas)
            dfdrawdowns = drawdowns_df(dfinputmetricas)
            sedrawdownsestats, lsmetricas = drawdowns_estats(dfdrawdowns, lsmetricas)
            dfdiasout = dias_out_df(dfinputmetricas)
            sediasoutestats, lsmetricas = dias_out_estats(dfdiasout, lsmetricas)
            dfstopdrawdown = stop_drawdown_df(dfindexdrawdown)
            sestopdrawdownestats, lsmetricas = stop_drawdown_estats(dfstopdrawdown, lsmetricas)

            return lsmetricas

        except Exception as e:
            print(f"⚠️ Erro ao processar índice {il}: {e}")
            traceback.print_exc()
            return None

    # Prepara os argumentos para cada linha
    args_list = [
        (il, dfparamtest.iloc[il], dftitulosdados, srbacktest['dataini'], srbacktest['datafim'])
        for il in dfparamtest.index
    ]

    # Executa em paralelo
    resultados = []
    with ThreadPoolExecutor() as executor:
        for resultado in executor.map(processar_parametros, args_list):
            if resultado is not None:
                resultados.append(resultado)

    # Atualiza dfmetricas com os resultados válidos
    for lsmetricas in resultados:
        dfmetricas = atualizar_df_metricas(dfmetricas, lsmetricas)

    return dfmetricas



#Almacena os dados de dfmetricas no BD sqTradeSys

import sqlite3
def dfmetricas_a_sqTadeSys (df, nome_banco, nome_tabela):
    conn = sqlite3.connect(nome_banco)
    cursor = conn.cursor()

    # Verifica se a tabela existe
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{nome_tabela}'")
    tabela_existe = cursor.fetchone() is not None

    # Se existir, verifica os id_backtest já presentes
    ids_existentes = set()
    if tabela_existe:
        try:
            cursor.execute(f"SELECT DISTINCT id_backtest FROM {nome_tabela}")
            ids_existentes = {linha[0] for linha in cursor.fetchall()}
        except sqlite3.OperationalError:
            pass  # Coluna ainda não existe

    # Filtra o DataFrame para excluir registros já existentes
    df_filtrado = df[~df['id_backtest'].isin(ids_existentes)]

    if df_filtrado.empty:
        print("⚠️ Nenhum novo registro para inserir. Todos os id_backtest já existem.")
        conn.close()
        return

    # Verifica e adiciona colunas faltantes
    if tabela_existe:
        cursor.execute(f"PRAGMA table_info({nome_tabela})")
        colunas_existentes = [linha[1] for linha in cursor.fetchall()]

        for coluna in df_filtrado.columns:
            if coluna not in colunas_existentes:
                tipo = "TEXT"
                if df_filtrado[coluna].dtype == "int64":
                    tipo = "INTEGER"
                elif df_filtrado[coluna].dtype == "float64":
                    tipo = "REAL"
                cursor.execute(f"ALTER TABLE {nome_tabela} ADD COLUMN {coluna} {tipo}")
    else:
        # Cria a tabela com todas as colunas
        df_filtrado.head(0).to_sql(nome_tabela, conn, if_exists='replace', index=False)

    # Insere os dados filtrados
    df_filtrado.to_sql(nome_tabela, conn, if_exists='append', index=False)

    conn.commit()
    conn.close()
    print(f"✅ {len(df_filtrado)} novos registros inseridos na tabela '{nome_tabela}'.")

