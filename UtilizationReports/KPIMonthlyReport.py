import datetime
import sys
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import KPIUtils

class KPIMonthly:
    def __init__(self):
        #self.MailList=['yair.bloom@xjet3d.com','dorothee.moshevich@xjet3d.com']
        self.MailList=['yair.bloom@xjet3d.com']
        Now=datetime.datetime.now() 
        self.StartTime = datetime.datetime(2018, 1, 1)
        self.EndTime = datetime.datetime(Now.year , Now.month ,1) 
 
    def Exec(self):
        try:
            

            HtmlStr = "<html><head></head><body>"
            UtilizationSummary={}
            MonthStrList=[]
           
            CurentTime = self.StartTime
            while CurentTime <  self.EndTime:
                NextMonthTime =   datetime.datetime(CurentTime.year+ CurentTime.month/12 , CurentTime.month%12+1, 1)
                MR=KPIUtils.CKPIUtils()
                MonthSum = MR.GetUtilizationInfo(CurentTime , NextMonthTime)
                MonthStrList.append(CurentTime.strftime("%B %y"))
                UtilizationSummary[MonthStrList[-1]] = pd.Series(MonthSum['Utilization (precent)'],index=MonthSum['Machine Name'])
                HtmlStr += "<h3>Machines Utilization Summary for <i> %s </i></h3><br><br> %s <br><br>"%(CurentTime.strftime("%B") ,pd.DataFrame.from_dict(MonthSum).to_html())
                CurentTime = NextMonthTime
            HtmlStr+="</body></html>"

            UtilizationCsvStr=(pd.DataFrame.from_dict(UtilizationSummary).to_csv(columns=MonthStrList))
            MR.SendMail(MailList = self.MailList , Subject='KPI Report' , HtmlStr=HtmlStr ,CsvStr=UtilizationCsvStr , CsvFileName='KPI.csv')
        except Exception as err:
            print str(err)
            pass


if __name__ == '__main__':
  amMachineUtilization = KPIMonthly()
  amMachineUtilization.Exec()


