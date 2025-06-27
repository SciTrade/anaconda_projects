from datetime import date, datetime
import pandas as pd
import yfinance as yf
import time
import schedule
from Alert import Alert
pd.options.mode.chained_assignment = None  # default='warn'

DATAPATH = "./"
ERRORFILE_PATH = "C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\alert15m_errors.txt"
LASTALERT_PATH = "C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\lastAlert_15m.csv"
LASTCHECK_PATH = "C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\lastCheckedTime.txt"
OPEN_MARKET_HOUR = 9
CLOSE_MARKET_HOUR = 18

alert = Alert('15m')

def run_test():
    print("Running test...")

    try: 
        # Get last record closed
        df = yf.download(tickers='GGAL', period='60d', interval='15m')
        df = df.iloc[:-2 , :]

        # Stochastic calculation
        df = alert.set_test(df, "15m")

        # Get last time row checked and compare
        lastTime = df.iloc[-1].time
        with open(LASTCHECK_PATH, 'r') as f:
            lastTimeChecked = f.read()

        # If it's a new row, check if there is an alert
        if(lastTimeChecked != lastTime.strftime("%Y-%m-%d %H:%M:%S")):
            check_alert(df)
        else:
            print('Row already registered.')
        
    except Exception as e:
        alert.handle_error(e, ERRORFILE_PATH)

    finally:
        print("Test finished")
        last = df.iloc[-1]
        print("Time: ", last.timeArg)
        print("Estado: ", last.state.upper())

        # Write last row checked time to file
        with open(LASTCHECK_PATH, 'w') as f:
            f.write(last.time.strftime("%Y-%m-%d %H:%M:%S"))


def notify_status():
    print("Running status test...")

    # Get last record closed
    try: 
        df = yf.download(tickers='GGAL', period='60d', interval='15m')
        df = df.iloc[:-2 , :]

        # Stochastic calculation
        df = alert.set_test(df, "15m")

        # Signals
        alert.set_status_mail(df.iloc[-1], '15m')

        # Get status excel
        odate = df.iloc[-1].time.strftime("%d-%m-%Y_%H%M%S")
        alert.get_excel(df, f"C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\status\\status_15m_{ odate }.xlsx")

    except Exception as e:
        alert.handle_error(e, ERRORFILE_PATH)

    finally:
        print("Status test finished")


def check_missing_alerts(df):
    try:
        last = df.iloc[-1]

        # Read last alert csv
        lastAlert = alert.read_alert_csv(LASTALERT_PATH)

        # Compare states
        if lastAlert.oper == 'CLOSELONG' or lastAlert.oper == 'CLOSESHORT':
            lastState = 'neutro'
            if(lastState != last.state):
                print("Previous state: ", lastState)
                print("Current state: ", last.state)
                lastOperCompra = df[df['oper'] == 'COMPRA'].iloc[-1]
                lastOperVenta = df[df['oper'] == 'VENTA'].iloc[-1]
                missingAlert = lastOperCompra if lastOperCompra.time > lastOperVenta.time else lastOperVenta
                alert.set_alert_mail(missingAlert, '15m')
                missingAlert.to_csv(LASTALERT_PATH)
        elif lastAlert.oper == 'COMPRA' or lastAlert.oper == 'VENTA':
            lastState = lastAlert.oper.lower()
            if(lastState != last.state):  
                print("Previous state: ", lastState)
                print("Current state: ", last.state)
                lastOperCloseLong = df[df['oper'] == 'CLOSELONG'].iloc[-1]
                lastOperCloseShort = df[df['oper'] == 'CLOSESHORT'].iloc[-1]
                missingAlert = lastOperCloseLong if lastOperCloseLong.time > lastOperCloseShort.time else lastOperCloseShort
                alert.set_alert_mail(missingAlert, '15m')
                missingAlert.to_csv(LASTALERT_PATH)
    except Exception as e:
        alert.handle_error(e, ERRORFILE_PATH)


def check_alert(df):

    # Check if there is a missing alert
    check_missing_alerts(df)

    try:
        last = df.iloc[-1]
        if(last.oper):
            if alert.was_lastAlert_sent(last, LASTALERT_PATH):
                print(last.timeArg, '-', last.oper, ": Alert already sent")
            else:
                alert.set_alert_mail(last, '15m')
                last.to_csv(LASTALERT_PATH)

            odate = last.time.strftime("%d-%m-%Y_%H%M%S")
            alert.get_excel(df, f"C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\status\\status_15m_ALERT_{odate}.xlsx")

    except Exception as e:
        alert.handle_error(e, ERRORFILE_PATH)


def main(): 

    df = yf.download(tickers='GGAL', period='60d', interval='15m')
    df = df.iloc[:-2 , :]

    # df = alert.set_test(df, "15m")
    # check_missing_alerts(df)

    schedule.every(3).minutes.do(run_test)
    schedule.every(50).minutes.do(notify_status)

    while True:
        schedule.run_pending()
        time.sleep(1)
        if (datetime.now().hour >= CLOSE_MARKET_HOUR or datetime.now().hour <= OPEN_MARKET_HOUR or
            date.today().weekday() == 6 or date.today().weekday() == 5):
            exit()


if __name__ == '__main__':
    main()