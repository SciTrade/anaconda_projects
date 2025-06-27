from datetime import date
import pandas as pd
from Alert import Alert 
import yfinance as yf
from pandas.tseries.offsets import DateOffset
pd.options.mode.chained_assignment = None  # default='warn'

def set_results(df):
    df['resultado'] = 0.
    ultimo = 0.
    
    for i in df.index[::-1]:

        if df.loc[i, 'oper'] == 'CLOSELONG':
            ultimo = df.loc[i, 'long']
        elif df.loc[i, "oper"] == 'CLOSESHORT':
            ultimo = df.loc[i, 'short']
        elif df.loc[i, 'oper'] == 'COMPRA':
            if(not pd.isnull(df.loc[i, 'short'])):
                ultimo = df.loc[i, 'short']
        elif df.loc[i, "oper"] == 'VENTA':
            if(not pd.isnull(df.loc[i, 'long'])):
                ultimo = df.loc[i, 'long']
            
        df.loc[i, 'resultado'] = ultimo
        
    
def set_index(df):
    df['indice'] = 1.
    df['posicion'] = 0.

    posicion = 0.
    entrada_short = 0.
#    comision = 0.0075
    comision = 0.
    lastActual = 1000.

    actual = 1000.
    
    for i in df.index:
        if posicion > 0.:
            actual = posicion * df.loc[i, 'Close']
        elif posicion < 0.:
            actual = (- posicion * 
                    (2. * entrada_short - df.loc[i, 'Close']))
        else:
            actual = lastActual
        
        if df.loc[i, 'oper'] == 'COMPRA':
            posicion = actual * ((1. - comision) /
               df.loc[i, 'Close'] / (1. + comision))
        elif df.loc[i, "oper"] == 'VENTA':
            posicion = - actual * ((1. - comision) /
                        df.loc[i, 'Close'] / (1. + comision))
            entrada_short = df.loc[i, 'Close']
        elif df.loc[i, 'oper'] == 'CLOSELONG' or df.loc[i, 'oper'] == 'CLOSESHORT':
            posicion = 0
            
        if posicion > 0.:
            actual = posicion * df.loc[i, 'Close']
        elif posicion < 0.:
            actual = (- posicion * 
                    (2. * entrada_short - df.loc[i, 'Close']))
        else: 
            if (actual == 0): actual = 1000.

        df.loc[i, 'indice'] = actual / 1000.
        df.loc[i, 'posicion'] = posicion
        lastActual = actual


        
def set_other_index(df):
    df['longInd'] = 1.
    df['shortInd'] = 1.
    df['longAcu'] = 1.
    df['shortAcu'] = 1.

    df['symbolAcu'] = 1.
    df['anualInd'] = 0.
    df['anualLong'] = 0.
    df['anualShort'] = 0.
    df['anualSym'] = 0.

    baseLong = 1.
    baseShort = 1.
    baseLongAcu = 1.
    baseShortAcu = 1.
    lastLongAcu = 1.
    lastShortAcu = 1.
    lastSymbolAcu = 1.
    lastClose = 0.
    
    long = False
    short = False
    
    for i in df.index:
        df.loc[i, 'symbolAcu'] = lastSymbolAcu * df.loc[i, 'Close'] / lastClose if lastClose != 0 else 1
        lastClose = df.loc[i, 'Close']
        lastSymbolAcu = df.loc[i, 'symbolAcu']

        if long:
            df.loc[i, 'longInd'] = \
                df.loc[i, 'indice'] / baseLong
            df.loc[i, 'longAcu'] = \
                df.loc[i, 'indice'] / baseLongAcu
            df.loc[i, 'shortAcu'] = lastShortAcu
        elif short:
            df.loc[i, 'shortInd'] = \
                df.loc[i, 'indice'] / baseShort
            df.loc[i, 'shortAcu'] = \
                df.loc[i, 'indice'] / baseShortAcu
            df.loc[i, 'longAcu'] = lastLongAcu
        else:
            df.loc[i, 'longAcu'] = lastLongAcu
            df.loc[i, 'shortAcu'] = lastShortAcu
               
        if df.loc[i, 'oper'] == 'COMPRA':
            long = True
            short = False
            baseLong = df.loc[i, 'indice']
            baseLongAcu = df.loc[i, 'indice'] / \
                lastLongAcu
            lastShortAcu = df.loc[i, 'shortAcu']
        elif df.loc[i, "oper"] == 'VENTA':
            short = True
            long = False
            baseShort = df.loc[i, 'indice']
            baseShortAcu = df.loc[i, 'indice'] / \
                lastShortAcu
            lastLongAcu = df.loc[i, 'longAcu']
        elif df.loc[i, 'oper'] == 'CLOSELONG':
            short = False
            long = False
            baseLong = df.loc[i, 'indice']
            baseLongAcu = df.loc[i, 'indice'] / \
                lastLongAcu
            lastLongAcu = df.loc[i, 'longAcu']
        elif df.loc[i, 'oper'] == 'CLOSESHORT':
            short = False
            long = False
            baseShort = df.loc[i, 'indice']
            baseShortAcu = df.loc[i, 'indice'] / \
                lastShortAcu
            lastShortAcu = df.loc[i, 'shortAcu']

        prev = i - DateOffset(years = 1)
        end = prev + DateOffset(days = 3)

        try:

            df.loc[i, 'anualInd'] = ( df.loc[i, 'indice'] /
                df.loc[prev:end, 'indice'].iloc[0])
            df.loc[i, 'anualLong'] = ( df.loc[i, 'longAcu'] /
                df.loc[prev:end, 'longAcu'].iloc[0])
            df.loc[i, 'anualShort'] = ( df.loc[i, 'shortAcu'] /
                df.loc[prev:end, 'shortAcu'].iloc[0])
            df.loc[i, 'anualSym'] = ( df.loc[i, 'symbolAcu'] /
                df.loc[prev:end, 'symbolAcu'].iloc[0])

        except:
            pass

alert = Alert('2m')

df = yf.download(tickers='GGAL', period='60d', interval='2m')
print(df)

df = df.iloc[:-2 , :]

# Stochastic calculation
df = alert.set_test(df, "2m")

set_results(df)
set_index(df)
set_other_index(df)

odate = df.iloc[-1].time.strftime("%d-%m-%Y_%H%M%S")
alert.get_excel(df, f"C:\\Users\\Federico Navos\\Desktop\\Python\\stochastic\\alerta_trade\\status\\status_2m_{ odate }.xlsx")