import pandas as pd
from Alert import Alert 
import yfinance as yf

period = '15m'
LASTALERT_PATH = f"C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\lastAlert_{period}.csv"
alert = Alert(period)

df = yf.download(tickers='GGAL', period='60d', interval=period)
df = df.iloc[:-2 , :]
df = alert.set_test(df, period)

# Get status excel
alert.get_excel(df, f"C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\status\\status_{period}_{round(df.iloc[-1].time.timestamp())}.xlsx")

lastOper = df[df['oper'] != ''].iloc[-1]
lastOper.time = pd.to_datetime(lastOper.time, utc=True)
lastOper.timeArg = lastOper.time.tz_convert('America/Argentina/Buenos_Aires')

print(lastOper.timeArg)
print(lastOper.oper, "ALERT was set", period)

lastOper.to_csv(LASTALERT_PATH)