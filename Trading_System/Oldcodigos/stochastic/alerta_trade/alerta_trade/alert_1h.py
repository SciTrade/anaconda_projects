#alert_1h.py 

from datetime import date, datetime
import pandas as pd
import yfinance as yf
import time
from Alert import Alert
pd.options.mode.chained_assignment = None  # default='warn'

DATAPATH = "./"
ERRORFILE_PATH = "C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\alert1h_errors.txt"
LASTALERT_PATH = "C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\lastAlert_1h.csv"
OPEN_MARKET_HOUR = 9
CLOSE_MARKET_HOUR = 18

alert = Alert('1h')


def check_missing_alerts(df):
    try:
        last = df.iloc[-1]                                                    #ultimo registro de df_pre

        # Read last alert csv
        lastAlert = alert.read_alert_csv(LASTALERT_PATH)                      # registro escrito no csv

        # Compare states
        if lastAlert.oper[0] == 'CLOSELONG' or lastAlert.oper[0] == 'CLOSESHORT':
            lastState = 'neutro'
            if(lastState != last.state):
                print("Previous state: ", lastState)
                print("Current state: ", last.state)
                lastOperCompra = df[df['oper'] == 'COMPRA'].iloc[-1]
                lastOperVenta = df[df['oper'] == 'VENTA'].iloc[-1]
                missingAlert = lastOperCompra if lastOperCompra.time > lastOperVenta.time else lastOperVenta
                alert.set_alert_mail(missingAlert, '1h')
                missingAlert.to_csv(LASTALERT_PATH)
        elif lastAlert.oper[0] == 'COMPRA' or lastAlert.oper[0] == 'VENTA':   #COMPRA
            lastState = lastAlert.oper[0].lower()                             #compra
            if(lastState != last.state):                                      #neutro
                print("Previous state: ", lastState)                          # Pevious state: compra
                print("Current state: ", last.state)                          # Current state: neutro
                lastOperCloseLong = df[df['oper'] == 'CLOSELONG'].iloc[-1]
                lastOperCloseShort = df[df['oper'] == 'CLOSESHORT'].iloc[-1]
                missingAlert = lastOperCloseLong if lastOperCloseLong.time > lastOperCloseShort.time else lastOperCloseShort
                alert.set_alert_mail(missingAlert, '1h')
                missingAlert.to_csv(LASTALERT_PATH)
    except Exception as e:
        alert.handle_error(e, ERRORFILE_PATH)


def notify(df):
    # Check if last state is different from current state to avoid missing alerts
    check_missing_alerts(df)
    
    # Send mail with current state
    last = df.iloc[-1]
    if(last.oper):
        if alert.was_lastAlert_sent(last, LASTALERT_PATH):
            print(last.timeArg, '-', last.oper, ": Alert already sent")
        else:
            alert.set_alert_mail(last, '1h')
            last.to_csv(LASTALERT_PATH)
    else:
        alert.set_status_mail(last, '1h')


def main(): 

    pre_df = yf.download(tickers='GGAL', period='200d', interval='1h')
    pre_df = pre_df.iloc[:-3 , :]

    pre_df = alert.set_test(pre_df, "1h")
    check_missing_alerts(pre_df)

    print("Previous state: ", pre_df.iloc[-1].state.upper())

    # Set frecuency
    frec = 3600

    while(True):
        if (datetime.now().hour >= CLOSE_MARKET_HOUR or datetime.now().hour <= OPEN_MARKET_HOUR or
            date.today().weekday() == 6 or date.today().weekday() == 5):
            exit()

        # Get last record
        try: 
            df = yf.download(tickers='GGAL', period='200d', interval='1h')
            df = df.iloc[:-2 , :]

            # Compare with last record
            if df.tail(1).index[0] == pre_df.tail(1).index[0]:
                print(df.tail(1).index[0])
                print(pre_df.tail(1).index[0])
                print('Same record')
                time.sleep(frec/10)
                continue
            pre_df = df

            # Stochastic calculation
            df = alert.set_test(df, "1h")

            notify(df)
            last = df.iloc[-1]
            print("Time: ", last.timeArg)
            print("Estado: ", last.state.upper())
            # Get status excel
            odate = last.time.strftime("%d-%m-%Y_%H%M%S")
            alert.get_excel(df,f"C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\status\\status_1h_{ odate }.xlsx")

            time.sleep(frec)    
            
        except Exception as e:
            alert.handle_error(e, ERRORFILE_PATH)
            time.sleep(frec/10)


if __name__ == '__main__':
    main()