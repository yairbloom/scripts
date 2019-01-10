import datetime
import sys
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import MonthlyReport

class AmMachineUtilization:
    def __init__(self):
        self.MailList=['yair.bloom@xjet3d.com','dorothee.moshevich@xjet3d.com']
        #self.MailList=['yair.bloom@xjet3d.com']
        self.ThisYear = 2018
 
    def Exec(self):
        try:
            

            TheHtml = "<html><head></head><body>"
            AllMonths={}
            for i in range (1,13):
                StartDay = datetime.datetime(self.ThisYear, i, 1)
                MR=MonthlyReport.CMonthlyReport(i , self.ThisYear)
                MonthSum = MR.FetchDataFromMachineDB()
                AllMonths[StartDay.strftime("%B")] = pd.Series(MonthSum['Utilization (precent)'],index=MonthSum['Machine Name'])
                TheHtml += "<h3>Machines Utilization Summary for <i> %s </i></h3><br><br> %s <br><br>"%(StartDay.strftime("%B") ,pd.DataFrame.from_dict(MonthSum).to_html())
            TheHtml+="</body></html>"
            UtilizationCsvStr=(pd.DataFrame.from_dict(AllMonths).to_csv(columns=[datetime.datetime(self.ThisYear, i, 1).strftime("%B") for i in range (1,13)]))
                 
            msg = MIMEMultipart()
            msg['Subject'] = "AM lab Utilization for 2018"

            s = smtplib.SMTP('pod51014.outlook.com',587)
            s.starttls()
            s.login('bugs@xjet3d.com', 'Bug12345')


            SepStr=''
            ToList=''
            for email in self.MailList:
                ToList = ToList+SepStr+email
                SepStr = ','
            msg['To'] = ToList
            part = MIMEText(TheHtml, 'html')
            msg.attach(part)
            part = MIMEBase('application', "octet-stream")
            part.set_payload(UtilizationCsvStr)
            part.add_header('Content-Disposition', 'attachment; filename="Utilization.csv"')
            msg.attach(part)
            s.sendmail('bugs@xjet3d.com', self.MailList , msg.as_string())
            s.quit()

        except Exception as err:
            print str(err)
      
            pass


if __name__ == '__main__':
  amMachineUtilization = AmMachineUtilization()
  amMachineUtilization.Exec()


