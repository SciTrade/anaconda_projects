import pandas as pd
import yfinance
from Alert import Alert 
pd.options.mode.chained_assignment = None  


period = '15m'
alert = Alert(period)

file = f"C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\lastAlert_{period}.csv"
fileHistorical = f"C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\historyAlerts_{period}.csv"

df = alert.read_alert_csv(file)

alert.set_alert_mail(df, period)
df.to_csv(file)