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
