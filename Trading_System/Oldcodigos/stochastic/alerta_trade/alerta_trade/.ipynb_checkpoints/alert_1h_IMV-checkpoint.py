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
        last = df.iloc[-1]

        # Read last alert csv
        lastAlert = alert.read_alert_csv(LASTALERT_PATH)

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
        elif lastAlert.oper[0] == 'COMPRA' or lastAlert.oper[0] == 'VENTA':
            lastState = lastAlert.oper[0].lower()
            if(lastState != last.state):  
                print("Previous state: ", lastState)
                print("Current state: ", last.state)
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


def get_df_IMVUSD(pre = False):
    if pre:
        df_GGALUSD = yf.download(tickers='GGAL', period='200d', interval='1h')
        df_GGALUSD = df_GGALUSD.iloc[:-3, :]

        df_GGALARS = yf.download(tickers='GGAL.BA', period='200d', interval='1h')
        df_GGALARS = df_GGALARS.iloc[:-3, :]

        df_IMVARS = yf.download(tickers='M.BA', period='200d', interval='1h')
        df_IMVARS = df_IMVARS.iloc[:-3, :]
    else:
        df_GGALUSD = yf.download(tickers='GGAL', period='200d', interval='1h')
        df_GGALUSD = df_GGALUSD.iloc[:-2, :]

        df_GGALARS = yf.download(tickers='GGAL.BA', period='200d', interval='1h')
        df_GGALARS = df_GGALARS.iloc[:-2, :]

        df_IMVARS = yf.download(tickers='M.BA', period='200d', interval='1h')
        df_IMVARS = df_IMVARS.iloc[:-2, :]

    df_GGALUSD = df_GGALUSD.resample('1h').mean()
    df_GGALUSD.index = df_GGALUSD.index.tz_convert('America/Argentina/Buenos_Aires')

    df = pd.DataFrame()
    df['Close'] = df_IMVARS['Close']/((df_GGALARS['Close']/df_GGALUSD['Close'])*10)
    df['Open'] = df_IMVARS['Open']/((df_GGALARS['Open']/df_GGALUSD['Open'])*10)
    df['High'] = df_IMVARS['High']/((df_GGALARS['High']/df_GGALUSD['High'])*10)
    df['Low'] = df_IMVARS['Low']/((df_GGALARS['Low']/df_GGALUSD['Low'])*10)

    df.index = df.index.tz_localize(None)
    df = df.dropna(subset=['Close'])

    return df


def main(): 

    pre_df = get_df_IMVUSD(pre = True)

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
            df = get_df_IMVUSD()

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
            alert.get_excel(df, f"C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\status\\status_1h_{ odate }.xlsx")

            time.sleep(frec)    
            
        except Exception as e:
            alert.handle_error(e, ERRORFILE_PATH)
            time.sleep(frec/10)


if __name__ == '__main__':
    main()