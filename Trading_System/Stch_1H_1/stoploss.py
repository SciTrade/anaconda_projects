
#stop_loss_reentry

def stop_loss_reentry (dfsignals, stpl) :                 #Columns: datetime,open,high,low,close,volume,state
    import pandas as pd
    df = dfsignals[(dfsignals['state'] == 'enter') | (dfsignals['state'] == 'stay')]
    df = df.reset_index(drop=True)
    
    
    df["stpl"] = 0.0
    stoplossprice = 0.0
    lastlongbuyprice = 0.0

    for i in range(0, len(df)):
        
        if df.loc[i, "state"] == "enter" :
           stoplossprice = df.loc[i, "close"]
           df.loc[i,"stpl"] = df.loc[i, "close"] - stoplossprice * (1 - stpl)
           
        if df.loc[i, "state"]== "stay" :
           df.loc[i, "stpl"] = df.loc[i, "close"] - stoplossprice * (1- stpl)
            
           if df.loc[i, "stpl"] < 0.0 :
                df.loc[i, "state"] = "out"
               
           if df.loc[i, "stpl"] > 0.0 and   (df.loc[i-1, "state"] == "out" or df.loc[i-1, "state"] == "outstpl") :
                df.loc[i, "state"] = "enter"
               
           if df.loc[i, "stpl"] < 0.0 and   (df.loc[i-1, "state"] == "out" or df.loc[i-1, "state"] == "outstpl") :
                df.loc[i, "state"] = "outstpl"
    dfstoploss = df

    # reensablar e limpar duplicados out dfsignals 
    dfsignalsout = dfsignals[(dfsignals['state'] == 'out')]
     # elimino a culuna stpl de dfstoploss e filtro os valores enter e out 
    dfstoplossdrop = dfstoploss.drop(columns=["stpl"]) 
    dfstoplossenterout = dfstoplossdrop[(dfstoplossdrop['state'] == 'enter') | (dfstoplossdrop['state'] == 'out')]

    # concatenar os dois df para ter o total dos signals enter e out
    dfsignalsenterout = pd.concat([dfsignalsout, dfstoplossenterout], ignore_index=True) 
    # Ordenar pelo datetime e resetear o index
    dfsignalsenterout["datetime"] = pd.to_datetime(dfsignalsenterout["datetime"])
    dfsignalsenterout = dfsignalsenterout.sort_values("datetime").reset_index(drop=True)

    # limpar os out duplicados"out" por a saida anticipada do stoploss e reiniciar indice
    df = dfsignalsenterout
    cond = (df["state"] == "out")  & (df["state"].shift(1) == "out")
    dfsignals = df[~cond].reset_index(drop=True)
    
    return dfsignals , dfstoploss  #Columns: datetime,open,high,low,close,volume,state


# Stop drawdown Calculation , "stopsys" asignation into state column

def stop_drawdown_simple (dfindex, drawmax): #dfindex columns: datetime, open,high,low,close,volume,state,index_sc,trade,index
    import pandas as pd
    df = dfindex
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["index"] = pd.to_numeric(df["index"], errors="coerce")

    estado_corrigido = []
    pico_atual = df.loc[0, "index"]

    for i in range(len(df)):
        valor_index = df.loc[i, "index"]
        estado = df.loc[i, "state"]

        # Atualiza pico se houve recuperação
        if valor_index > pico_atual:
            pico_atual = valor_index

        # Calcula drawdown
        if pico_atual > 0:
            drawdown = (valor_index - pico_atual) / pico_atual
        else:
            drawdown = 0

        # Verifica se deve aplicar stopsys
        if estado == "out" and drawdown < (- drawmax):
            estado = "stopsys"
            pico_atual = valor_index  # reinicia ciclo a partir desse ponto

        estado_corrigido.append(estado)
    df["state"] = estado_corrigido
    dfindexdrawdown = df
    return dfindexdrawdown
