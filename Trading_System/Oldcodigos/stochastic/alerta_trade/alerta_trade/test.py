from datetime import date
import pandas as pd
from Alert import Alert 
import yfinance as yf
pd.options.mode.chained_assignment = None  # default='warn'

symbol = "BTC-USD"
period = "1h"

alert = Alert(period)

if (period == "1h"):
    df = yf.download(tickers=symbol, period='200d', interval=period)
else:
    df = yf.download(tickers=symbol, period='60d', interval=period)

print(df)
print(len(df))
df.index = df.index.tz_localize(None)
df.to_excel("BTC_yf.xlsx")