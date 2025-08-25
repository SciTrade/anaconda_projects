import pandas as pd
# Tir total calculation
def tir_total_anualizada(dfinputmetricas, lsmetricas):
    import pandas as pd
    df = dfinputmetricas
    # Garante que datetime está no formato certo
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Filtra enter e out
    df_enter = df[df['state'] == 'enter']
    df_out = df[df['state'] == 'out']

    # Verificação
    if df_enter.empty or df_out.empty:
        return None

    # Índice inicial e final
    idx_inicio = df_enter.iloc[0]['index']
    idx_fim = df_out.iloc[-1]['index']

    # Período completo entre primeira e última data do DataFrame
    dt_inicio_total = df['datetime'].min()
    dt_fim_total = df['datetime'].max()
    dias_total = (dt_fim_total - dt_inicio_total).days

    # Validação
    if dias_total <= 0 or idx_inicio == 0:
        return None

    # TIR anualizada com base no período total do df
    tirtotalanual = (idx_fim / idx_inicio) ** (365 / dias_total) - 1
    setirtotalanual = pd.Series({'tirtotalanual': tirtotalanual})
    lsmetricas.append (setirtotalanual)
    return  setirtotalanual , lsmetricas



#Tir Anuais Metrics
# dataframe  calculation
def tir_anuais_df (dfinputmetricas, dataini, datafim):

    # Exemplo do DataFrame original
    df = dfinputmetricas
    dataini = pd.to_datetime(dataini)
    datafim = pd.to_datetime(datafim)
    
    # Lista para novos registros
    novos_registros = []
    
    # Verifica se dataini deve ser adicionado
    if dataini < df.iloc[0]['datetime']:
        novos_registros.append({
            'datetime': dataini,
            'state': '',
            'index': df.iloc[0]['index']
        })
    
    # Verifica se datafim deve ser adicionado
    if datafim > df.iloc[-1]['datetime']:
        novos_registros.append({
            'datetime': datafim,
            'state': '',
            'index': df.iloc[-1]['index']
        })
    
    # Adiciona os registros e ordena
    df = pd.concat([pd.DataFrame(novos_registros), df], ignore_index=True)
    df = df.sort_values(by='datetime').reset_index(drop=True)
    
    # Determina os anos, excluindo o último ano
    ano_inicial = df['datetime'].min().year
    ano_final = (df['datetime'].max().year)
    
    # Gera os anos do intervalo EXCLUINDO o último ano
    anos_validos = range(ano_inicial, ano_final-1 )  # << ajuste aqui
    
    # Lista para os novos registros
    novos_registros = []
    
    for ano in anos_validos:
        fim_do_ano = pd.to_datetime(f'{ano}-12-31 23:59:59')
        df_antes = df[df['datetime'] < fim_do_ano]
        if not df_antes.empty:
            index_valor = df_antes.iloc[-1]['index']
            novos_registros.append({
                'datetime': fim_do_ano,
                'state': '',
                'index': index_valor
            })
    
    # Adiciona e organiza
    df = pd.concat([df, pd.DataFrame(novos_registros)], ignore_index=True)
    df = df.sort_values('datetime').reset_index(drop=True)
    
    # calcula o dataframe com as tir anuales ao fim do ano , com os anos incompletos anualizadas
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    #  consolidar por dia e manter o último registro
    df['date'] = df['datetime'].dt.date
    df_diario = df.sort_values('datetime').groupby('date', as_index=False).last()
    
    #  selecionar datas de fim de ano
    df_fim_ano = df_diario[
        (pd.to_datetime(df_diario['date']).dt.month == 12) &
        (pd.to_datetime(df_diario['date']).dt.day == 31)
    ].copy()
    
    #  calcular TIR entre pares de fim de ano
    resultados = []
    
    for i in range(1, len(df_fim_ano)):
        dt_inicio = pd.to_datetime(df_fim_ano.iloc[i - 1]['date'])
        dt_fim = pd.to_datetime(df_fim_ano.iloc[i]['date'])
        idx_inicio = df_fim_ano.iloc[i - 1]['index']
        idx_fim = df_fim_ano.iloc[i]['index']
        dias = (dt_fim - dt_inicio).days
    
        if dias > 0 and idx_inicio != 0:
            tir = (idx_fim / idx_inicio) ** (365 / dias) - 1
            resultados.append({
                'datetime': dt_fim,
                'tiranual': tir
            })
    
    #  adicionar último intervalo incompleto
    if not df_fim_ano.empty:
        dt_inicio = pd.to_datetime(df_fim_ano.iloc[-1]['date'])
        idx_inicio = df_fim_ano.iloc[-1]['index']
        dt_fim = pd.to_datetime(df_diario.iloc[-1]['date'])
        idx_fim = df_diario.iloc[-1]['index']
        dias = (dt_fim - dt_inicio).days
    
        if dias > 0 and idx_inicio != 0:
            tir = (idx_fim / idx_inicio) ** (365 / dias) - 1
            resultados.append({
                'datetime': dt_fim,
                'tiranual': tir
            })

    # criar DataFrame final
    dftiranual = pd.DataFrame(resultados)
    return dftiranual

#estatistic calculation
def tir_anuais_estats(dftiranual, lsmetricas):
    tir = dftiranual['tiranual'].dropna()

    estatisticas = {
        'tiranualquant': tir.count(),
        'tiranualfirst': round(tir.iloc[0], 6),
        'tiranualmedia': round(tir.mean(), 6),
        'tiranualmax': round(tir.max(), 6),
        'tiranualmin': round(tir.min(), 6),
        'tiranualstd': round(tir.std(), 6)
    }
    setiranuaisestats = pd.Series(estatisticas)
    lsmetricas.append (setiranuaisestats)
    return setiranuaisestats , lsmetricas

                        #TRADES METRICS

# trades estatistics calculation
def trades_estats(dfinputmetricas, lsmetricas):
    df = dfinputmetricas.copy()
    trades = df["trade"].dropna()

    positivos = trades[trades > 0]
    negativos = trades[trades < 0]

    # Porcentagem de positivos
    porcentagem_pos = (len(positivos) / len(trades)) if len(trades) > 0 else 0

    ditradesestat = {
        "tradestot": len(trades),
        'tradefirst': round(trades.iloc[1], 6),
        "tradespositpor": round(porcentagem_pos, 6),
        "tradesposmedia": round(positivos.mean(), 6) if not positivos.empty else None,
        "tradesposstd": round(positivos.std(), 6) if not positivos.empty else None,
        "tradesposmax": round(positivos.max(), 6) if not positivos.empty else None,
        "tradesposmin": round(positivos.min(), 6) if not positivos.empty else None
    }

    setradesestats = pd.Series(ditradesestat)
    lsmetricas.append (setradesestats)
    return setradesestats , lsmetricas



#Drawdown Metrics

#Dataframe Drawdown Calculation
def drawdowns_df (dfinputmetricas):
   
    df = dfinputmetricas
    df["datetime"] = pd.to_datetime(df["datetime"])
    serie = df["index"].dropna().reset_index(drop=True)
    datas = df["datetime"].reset_index(drop=True)

    drawdowns = []

    pico_idx = 0
    pico = serie[0]
    vale_idx = None
    valor_vale = None
    max_dd = 0

    for i in range(1, len(serie)):
        if serie[i] > pico:
            # Se recuperou acima do último pico: salvar ciclo anterior
            if vale_idx is not None and max_dd < 0:
                drawdowns.append({
                    "Data Pico": datas[pico_idx],
                    "Valor Pico": pico,
                    "Data Vale": datas[vale_idx],
                    "Valor Vale": valor_vale,
                    "Drawdown (%)": round(max_dd * 100, 2)
                })

            # Novo pico inicia novo ciclo
            pico = serie[i]
            pico_idx = i
            vale_idx = None
            max_dd = 0
        else:
            dd = (serie[i] - pico) / pico
            if dd < max_dd:
                max_dd = dd
                vale_idx = i
                valor_vale = serie[i]

    # Salva último ciclo, se aplicável
    if vale_idx is not None and max_dd < 0:
        drawdowns.append({
            "Data Pico": datas[pico_idx],
            "Valor Pico": pico,
            "Data Vale": datas[vale_idx],
            "Valor Vale": valor_vale,
            "Drawdown (%)": round(max_dd * 100, 2)
        })

    # Retorna os top N
    df_resultado = pd.DataFrame(drawdowns)
    return df_resultado.sort_values("Drawdown (%)").reset_index(drop=True)  

# Drawdowns statictics calculation
def drawdowns_estats(dfdrawdowns , lsmetricas):
    dd = dfdrawdowns['Drawdown (%)'].dropna()  # Filtra nulos, se houver

    estatisticas = {
        'drawdfirst': round(dd.iloc[0], 6),
        'drawdtot': dd.count(),
        'drawdmedia': round(dd.mean(), 2),
        'drawdmaximo': round(dd.max(), 2),
        'drawdminimo': round(dd.min(), 2),
        'drawdstd': round(dd.std(), 2)
    }
    sedrawdownsestats = pd.Series(estatisticas)
    lsmetricas.append (sedrawdownsestats)
    return sedrawdownsestats , lsmetricas



#Dias Out Metrics

# Dataframe calculation
def dias_out_df (dfmetricas):    
    df = dfmetricas
    coluna="index_sc"
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df[df[coluna].notna()].reset_index(drop=True)

    variacao = df[coluna].diff()
    grupos = (variacao != 0).cumsum()

    agrupado = df.groupby(grupos)
    periodos_estaticos = []

    for _, grupo in agrupado:
        if len(grupo) > 1 and grupo[coluna].nunique() == 1:
            duracao_dias = (grupo["datetime"].iloc[-1] - grupo["datetime"].iloc[0]).days
            periodos_estaticos.append({                
                "Data Início": grupo["datetime"].iloc[0],
                "Data Fim": grupo["datetime"].iloc[-1],
                "difdias": duracao_dias,
                "Valor index": grupo[coluna].iloc[0]
            })

    dfdiasout = pd.DataFrame(periodos_estaticos)
    dfdiasout = dfdiasout.query("difdias != 0").copy()
    dfdiasout = dfdiasout.reset_index(drop=True)
    
    return dfdiasout
    


# Diasout statistic calculation and lsmetricas agregation
def dias_out_estats(dfdiasout, lsmetricas) :
    dias = dfdiasout['difdias'].dropna()  # Remove valores nulos, se houver

    estatisticas = {
        'diasoutfirst': round(dias.iloc[0], 6),
        'diasouttot': dias.sum(),
        'diasoutmedia': round(dias.mean(), 2),
        'diasoutmax': dias.max(),
        'diasoutmin': dias.min(),
        'diasoutstd': round(dias.std(), 2)
    }
    sediasoutestats = pd.Series(estatisticas)
    lsmetricas.append(sediasoutestats)    
    return sediasoutestats, lsmetricas



#Metrica StopSys

# Dataframe calculation
def stop_drawdown_df (dfindexdrawdown) : 
    df = dfindexdrawdown
    # Garante que a coluna 'datetime' esteja no formato correto
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Filtra os registros onde state == 'stopsys'
    dfstopsys = df[df['state'] == 'stopsys'][['datetime', 'state', 'index']].copy()
    
    #  Ordena por datetime
    dfstopsys = dfstopsys.sort_values('datetime').reset_index(drop=True)
    return dfstopsys
    


# statistic dataframe based calculation and lsmetricas agregation
def stop_drawdown_estats(dfstopsys, lsmetricas):
    df = dfstopsys.copy()
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime').reset_index(drop=True)

    index_values = df['index'].dropna()

    if index_values.empty:
        estatisticas = {
            'stopsysfirst': 0.0,
            'stopsysquant': 0,
            'stopsysmedia': 0.0,
            'stopsysmaximo': 0.0,
            'stopsysminimo': 0.0,
            'stopsystd': 0.0
        }
    else:
        estatisticas = {
            'stopsysfirst': round(index_values.iloc[0], 6),
            'stopsysquant': index_values.count(),
            'stopsysmedia': round(index_values.mean(), 6),
            'stopsysmaximo': round(index_values.max(), 6),
            'stopsysminimo': round(index_values.min(), 6),
            'stopsystd': round(index_values.std(), 6)
        }

    sestopsysestats = pd.Series(estatisticas)
    lsmetricas.append(sestopsysestats)
    return sestopsysestats, lsmetricas
