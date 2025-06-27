from datetime import datetime
from email.message import EmailMessage
import os
import smtplib
import time
import traceback
import pandas as pd

class Alert():

    ERRORFILE_PATH = "C:\\Users\\gp\\Desktop\\Python\\stochastic\\alerta_trade\\alert_errors.txt"
    K = 16
    D = 8
    SMTH = 6  
    DAYM = 10
    SEMM = 3

# Constructor
    def __init__(self, per):  
        if per == "1h":
            self.K = 17
            self.D = 6
            self.SMTH = 8  
            self.DAYM = 7
            self.SEMM = 4 
        elif per == "2m":
            self.K = 16
            self.D = 8
            self.SMTH = 6  
            self.DAYM = 10
            self.SEMM = 3
        elif per == "15m":
            self.K = 9
            self.D = 5
            self.SMTH = 5  
            self.DAYM = 3
            self.SEMM = 8
    

# Df to excel function
    def get_excel(self, df, ofile):
        df.timeArg = df.timeArg.dt.tz_convert(None)

        writer = pd.ExcelWriter(ofile,
        engine='xlsxwriter',
        datetime_format='yyyy-mm-dd hh:mm')
        
        df.to_excel(writer, sheet_name='Datos', index=False)
        writer.save()

        print("Excel file created")


# Stochastic calculation
    def stochastic(self, df, i, K, D, smoth):
            
        df["k"] = (100. * (df.Close - df.Low.rolling(K).min()) /
            (df.High.rolling(K).max() - df.Low.rolling(K).min()))
        
        df["k" + i] = df.k.rolling(smoth).mean()
        df["d" + i] = df["k" + i].rolling(D).mean()
        
        df.drop(columns=["k"], inplace=True)  

        return df


# Set operations
    def set_compra(self, df, i):
        df.loc[i, "oper"] = "COMPRA"


    def set_venta(self, df, i):
        df.loc[i, "oper"] = "VENTA"


    def close_long(self, df, i, compra, venta):
        df.loc[i, "oper"] = "CLOSELONG"
        if compra !=0.:
            df.loc[i, "long"] = (venta - compra) / compra


    def close_short(self, df, i, compra, venta):
        df.loc[i, "oper"] = "CLOSESHORT"
        if venta !=0.:
            df.loc[i, "short"] = (venta - compra) / venta


# Set signals
    def set_signals(self, df):
        state = ""
        df["compra"] = False
        df["venta"] = False
        df["closeLong"] = False
        df["closeShort"] = False
        df["entradaLongH"] = False
        df["entradaShortH"] = False
        df["oper"] = ""
        df["long"] = ""
        df["short"] = ""
        df["state"] = "neutro"
        
        lastEntradaLongH = False
        lastEntradaShortH = False
        compra = 0.
        venta = 0.
        for i in df.index:
            l = df.loc[i]
            df.loc[i, "state"] = state

            if (l.khora > 20. and l.khora > l.dhora):
                df.loc[i, "entradaLongH"] = True
                if (not lastEntradaLongH):
                    if (l.kdia > 20. and l.kdia > l.ddia):
                        if(state == "venta"):
                            df.loc[i, "closeShort"] = True
                            state = "neutro"
                            compra = l.Close
                            self.close_short(df, i, compra, venta)
                        if (l.ksem > 80. or l.ksem > l.dsem):
                            df.loc[i, "compra"] = True
                            if state != "compra":
                                state = "compra"
                                compra = l.Close
                                self.set_compra(df, i)
            else:
                df.loc[i, "entradaLongH"] = False

            if (l.khora < 80. and l.khora < l.dhora):
                df.loc[i, "entradaShortH"] = True
                if (not lastEntradaShortH):
                    if(l.kdia < 80. and l.kdia < l.ddia):
                        if(state == "compra"):
                            df.loc[i, "closeLong"] = True
                            state = "neutro"
                            venta = l.Close
                            self.close_long(df, i, compra, venta)
                        if(l.ksem < 20. or l.ksem < l.dsem):
                            df.loc[i, "venta"] = True
                            if state != "venta":
                                state = "venta"
                                venta = l.Close
                                self.set_venta(df, i)
            else:
                df.loc[i, "entradaShortH"] = False

            lastEntradaLongH = df.loc[i, "entradaLongH"]
            lastEntradaShortH = df.loc[i, "entradaShortH"]
        
        return df


# Stochastic set up and signals calculation
    def set_test(self, df, period):
        if period == "1h":
            # Set params
            k = 17
            d = 6
            smth = 8  
            dayM = 7
            semM = 4
            self.K = 17
            self.D = 6
            self.SMTH = 8  
            self.DAYM = 7
            self.SEMM = 4 
        elif period == "2m":
            k = 16
            d = 8
            smth = 6  
            dayM = 10
            semM = 3
            self.K = 16
            self.D = 8
            self.SMTH = 6  
            self.DAYM = 10
            self.SEMM = 3
        elif period == "15m":
            k = 9
            d = 5
            smth = 5  
            dayM = 3
            semM = 8
            self.K = 9
            self.D = 5
            self.SMTH = 5  
            self.DAYM = 3
            self.SEMM = 8

        # Convert time
        df["time"] = pd.to_datetime(df.index, utc=True)
        df['timeArg'] = df['time'].dt.tz_convert('America/Argentina/Buenos_Aires')
        df['time'] = df['time'].dt.tz_convert(None)

        df = self.stochastic(df, "hora", k, d, smth)
        df = self.stochastic(df, "dia", k*dayM, d*dayM, smth*dayM)
        df = self.stochastic(df, "sem", k*dayM*semM, d*dayM*semM, smth*dayM*semM)
        df = self.set_signals(df)

        return df


# Handle error function
    def handle_error(self, e, ofile):
        with open(ofile, "a") as f:
            print(datetime.now(), file=f)
            traceback.print_exc(file=f)
            print('\n', file=f)
            traceback.print_exc()
        time.sleep(30)


# Return alert string
    def get_alert_oper(self, oper):
        if oper == 'COMPRA':
            return 'Entrar en LONG'
        elif oper == 'VENTA':
            return 'Entrar en SHORT'
        elif oper == 'CLOSELONG':
            return 'Salir de LONG'
        elif oper == 'CLOSESHORT':
            return 'Salir de SHORT'
        else:
            return ''


# Set up status mail and send it
    def set_status_mail(self, last, period):

        last.timeArg = pd.to_datetime(last.timeArg, utc=True)
        last.timeArg = last.timeArg.tz_convert('America/Argentina/Buenos_Aires')

        # Set message
        msg = EmailMessage()
        msg['Subject'] = f'Estado estocastico {period}'
        content = f"""\
        Estado estocastico {period}
        {last.timeArg}
        Close: { round(last.Close, 2) }

        Estado: { last.state.upper() }

        Sistema: [{self.K}-{self.D}-{self.SMTH}-{self.DAYM}-{self.SEMM}]
        Situacion actual:
        khora = {last['khora']}
        dhora = {last['dhora']}
        kdia = {last['kdia']}
        ddia = {last['ddia']}
        ksem = {last['ksem']}
        dsem = {last['dsem']}
        """
        msg.set_content(content)

        # Send mail
        self.send_mail(msg)


# Set up alert mail and send it
    def set_alert_mail(self, last, period):

        last.timeArg = pd.to_datetime(last.timeArg, utc=True)
        last.timeArg = last.timeArg.tz_convert('America/Argentina/Buenos_Aires')
        last.Close = float(last.Close)

        if((last.oper == 'COMPRA' and last.state == 'venta') or
            (last.oper == 'VENTA' and last.state == 'compra')):
            operacion = 'CLOSESHORT' if last.oper == 'COMPRA' else 'CLOSELONG'
            # Set message
            msg = EmailMessage()
            msg['Subject'] = f'{period.upper()}: Alerta trading - {operacion}'
            content = f"""\
            ALERTA TRADING {period}
            {last.timeArg}
            Close: { round(last.Close, 2) }

            Sistema: [{self.K}-{self.D}-{self.SMTH}-{self.DAYM}-{self.SEMM}]
            Señal de { self.get_alert_oper('CLOSESHORT') if last.oper == 'COMPRA' else self.get_alert_oper('CLOSELONG') }.
            Situacion actual:
            khora = {last['khora']}
            dhora = {last['dhora']}
            kdia = {last['kdia']}
            ddia = {last['ddia']}
            ksem = {last['ksem']}
            dsem = {last['dsem']}
            """
            msg.set_content(content)
            # Send mail
            self.send_mail(msg, True)
            print(f"TRADING ALERT. { last.timeArg }. { last.oper }.")

        operacion = last.oper
        if(last.oper == 'COMPRA'): operacion = 'LONG'
        if(last.oper == 'VENTA'): operacion = 'SHORT'
        # Set message
        msg = EmailMessage()
        msg['Subject'] = f'{period.upper()}: Alerta trading - {operacion}'
        content = f"""\
        ALERTA TRADING {period}
        {last.timeArg}
        Close: { round(last.Close, 2) }

        Sistema: [{self.K}-{self.D}-{self.SMTH}-{self.DAYM}-{self.SEMM}]
        Señal de { self.get_alert_oper(last.oper) }.
        Situacion actual:
        khora = {last['khora']}
        dhora = {last['dhora']}
        kdia = {last['kdia']}
        ddia = {last['ddia']}
        ksem = {last['ksem']}
        dsem = {last['dsem']}
        """
        msg.set_content(content)

        # Send mail
        self.send_mail(msg, True)
        print(f"TRADING ALERT. { last.timeArg }. { last.oper }.")


# Send mail function
    def send_mail(self, msg, alert=False):
        # Msg config
        if(alert):
            to = 'fedenavos@gmail.com'
            msg['To'] = to
            # to = ['fedenavos@gmail.com', 'rdmondaini@gmail.com', 'jxmxmx@hotmail.com']
            # msg['To'] = ', '.join(to)
        else:
            to = 'fedenavos@gmail.com'
            msg['To'] = to
            
        fromMail = 'alerta.trading.stochastic@gmail.com'
        msg['From'] = fromMail

        # Send mail function
        try:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls() # Secure the connection
            s.login(fromMail, 'jvttlupiiqobptky')
            s.send_message(msg)
            print('Mail sent')
        except Exception as e:
            self.handle_error(e, self.ERRORFILE_PATH)
        finally:
            s.quit() 


# Check if lastAlert is the same as the current alert
    def was_lastAlert_sent(self, last, file):
        if os.path.exists(file):
            lastAlert = self.read_alert_csv(file)
            return lastAlert['time'] == last['time']
        else:
            return False


# Read alert csv
    def read_alert_csv(self, file):
        lastAlert = pd.read_csv(file, delimiter=',', decimal='.')
        lastAlert = lastAlert.transpose()
        lastAlert.columns = lastAlert.iloc[0]
        lastAlert = lastAlert.iloc[1: , :]
        lastAlert = lastAlert.squeeze() 
        lastAlert.timeArg = pd.to_datetime(lastAlert.timeArg, utc=True)
        lastAlert.timeArg = lastAlert.timeArg.tz_convert('America/Argentina/Buenos_Aires')

        return lastAlert