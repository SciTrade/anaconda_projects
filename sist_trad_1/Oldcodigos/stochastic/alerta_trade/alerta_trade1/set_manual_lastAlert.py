import pandas as pd
from Alert import Alert 
import yfinance as yf

period = '15m'
LASTALERT_PATH = f"C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\lastAlert_{period}.csv"
alert = Alert(period)

if period == '2m':
    df = yf.download(tickers='GGAL', period='60d', interval='2m')
    df = alert.set_test(df, "2m")
elif period == '15m':
    df = yf.download(tickers='GGAL', period='60d', interval='15m')
    df = alert.set_test(df, "15m")
elif period == '1h':
    df = yf.download(tickers='GGAL', period='200d', interval='1h')
    df = alert.set_test(df, "1h")

# Get status excel
alert.get_excel(df, f"C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\status\\status_{period}_{round(df.iloc[-1].time.timestamp())}.xlsx")

lastOper = df[df['oper'] != ''].iloc[-1]
lastOper.time = pd.to_datetime(lastOper.time, utc=True)
lastOper.timeArg = lastOper.time.tz_convert('America/Argentina/Buenos_Aires')

print(lastOper.timeArg)
print(lastOper.oper, "ALERT was set", period)

lastOper.to_csv(LASTALERT_PATH)

