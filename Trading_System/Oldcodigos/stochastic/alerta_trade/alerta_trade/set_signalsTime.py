from datetime import date
import pandas as pd
from Alert import Alert 
import yfinance as yf
pd.options.mode.chained_assignment = None  # default='warn'

period = "2m"
SIGNALS_PATH = f"C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\signalsTime_{period}.csv"

alert = Alert(period)

df = yf.download(tickers='GGAL', period='60d', interval='2m')
print(df)

df = df.iloc[:-2 , :]

# Stochastic calculation
df = alert.set_test(df, "2m")

signals = df[df['oper'] != ''].time
print(signals)
signals.to_csv(SIGNALS_PATH)