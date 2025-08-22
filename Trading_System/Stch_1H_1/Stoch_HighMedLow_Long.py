# Trading system: Stoch_HighMedLow_Long

import numpy as np
import pandas as pd

# Stochastic calculation
def stochastic(dftitulosdados, i, K, D, smoth):
    df = dftitulosdados.copy()
    df["k"] = (100. * (df.close - df.low.rolling(K).min()) /
               (df.high.rolling(K).max() - df.low.rolling(K).min()))
    
    df["k" + i] = df["k"].rolling(smoth).mean()
    df["d" + i] = df["k" + i].rolling(D).mean()
    
    df.drop(columns=["k"], inplace=True)
    return df

# Stochastic high, med and low frequency
def stoch_hml(dfstoch, k, d, smth, medM, lowM):
    df = dfstoch.copy()
    df = stochastic(df, "high", k, d, smth)
    df = stochastic(df, "med", k * medM, d * medM, smth * medM)
    df = stochastic(df, "low", k * medM * lowM, d * medM * lowM, smth * medM * lowM)
    return df

# Criteria calculation
def system_criterias(dfstoch_hml):
    df = dfstoch_hml.copy()
    df["longbuylow"] = ((df["klow"] > 20) & (df["klow"] > df["dlow"])).astype(int)
    df["longbuymed"] = ((df["kmed"] > 20) & (df["kmed"] > df["dmed"])).astype(int)
    df["longbuyhigh"] = ((df["khigh"] > 20) & (df["khigh"] > df["dhigh"])).astype(int)
    return df

# Signal generation
def system_signals(dfcriterias):
    df = dfcriterias.copy()
    n = len(df)
    state_array = np.full(n, "standby", dtype=object)
    estado_anterior = "standby"

    high = df["longbuyhigh"].to_numpy()
    med = df["longbuymed"].to_numpy()
    low = df["longbuylow"].to_numpy()

    for i in range(1, n):
        if high[i] == 1 and med[i] == 1 and low[i] == 1 and estado_anterior == "standby":
            state_array[i] = "enter"
            estado_anterior = "enter"
        elif med[i] == 1 and low[i] == 1 and estado_anterior in ["enter", "stay"]:
            state_array[i] = "stay"
            estado_anterior = "stay"
        elif high[i] == 1 and low[i] == 1 and med[i] == 0 and estado_anterior in ["enter", "stay"]:
            state_array[i] = "stay"
            estado_anterior = "stay"
        elif low[i] == 0 and estado_anterior in ["enter", "stay"]:
            state_array[i] = "out"
            estado_anterior = "out"
        elif high[i] == 0 and med[i] == 0 and estado_anterior in ["enter", "stay"]:
            state_array[i] = "out"
            estado_anterior = "out"
        elif (low[i] == 0 or med[i] == 0) and estado_anterior == "out":
            state_array[i] = "standby"
            estado_anterior = "standby"
        else:
            state_array[i] = estado_anterior

    df["state"] = state_array
    dfsignals = df.drop(columns=[
        "khigh", "dhigh", "kmed", "dmed", "klow", "dlow",
        "longbuylow", "longbuymed", "longbuyhigh"
    ])
    return dfsignals

def Stoch_HighMedLow_Long (dftitulosdados, K, D, smoth, medM , lowM):     #Columns: datetime,open,high,low,close,volume 
    dfstoch = stochastic(dftitulosdados, 'high', K, D, smoth)
    dfstoch_hml= stoch_hml(dfstoch , K, D, smoth, medM , lowM )
    dfcriterias = system_criterias (dfstoch_hml)
    dfsignals = system_signals (dfcriterias)
    return dfsignals                      #Columns: datetime,open,high,low,close,volume,state
