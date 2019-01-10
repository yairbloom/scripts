#@PlatformDistribution:Carousel
import mysql.connector
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import sys
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import KPIUtils

class KPIWeekly:
    def __init__(self):
        
        self.TotalHoursTime =15 + 24 + 24 + 24 +24 + 14 #Sun 9:00 - Fri 14:00
        self.HourStartingOnSunday = 9
        #self.MailList=['yair.bloom@xjet3d.com','lior.lavid@xjet3d.com','nir.sade@xjet3d.com','dorothee.moshevich@xjet3d.com','ophira.melamed@xjet3d.com']
        self.MailList=['yair.bloom@xjet3d.com']
 
    def Exec(self):
        try:
            Now= datetime.now()
            StartTime = Now-timedelta(days=(Now.weekday()+1))
            StartTime = datetime(StartTime.year , StartTime.month , StartTime.day , self.HourStartingOnSunday)
            EndTime = StartTime + timedelta(seconds=self.TotalHoursTime*3600)

            HtmlStr = "<html><head></head><body><h3>Machines Utilization Summary from %s to %s</h3>"%(StartTime.strftime('%Y-%m-%d %H:%M:%S') ,  EndTime.strftime('%Y-%m-%d %H:%M:%S'))
            RowDataHtml='<h3>Row start/stop time events</h3>'
            FilterdDataHtml='<h3>Filtered start/stop time events</h3>'


            MR=KPIUtils.CKPIUtils()
            WeeklySummary = MR.GetUtilizationInfo(StartTime , EndTime , ReturnRowEvents=True)
            for i in range(len(WeeklySummary['Raw Data'])):
                RowDataHtml+= '<br><br>'
                RowDataHtml+= 'Machine Name%s<br>'%(WeeklySummary['Machine Name'][i])
                RowDataHtml+= 'Start time events: %s <br>'%(','.join(WeeklySummary['Raw Data'][i][10]))
                RowDataHtml+= 'Stop time events: %s <br>'%(','.join(WeeklySummary['Raw Data'][i][11]))
            for i in range(len(WeeklySummary['Filterd Data'])):
                FilterdDataHtml+= '<br><br>'
                FilterdDataHtml+= 'Machine Name: \%s<br>'%(WeeklySummary['Machine Name'][i])
                FilterdDataHtml+= '%s'%(WeeklySummary['Filterd Data'][i]).to_html()
      
            del WeeklySummary['Filterd Data']
            del WeeklySummary['Raw Data']
            HtmlStr+=pd.DataFrame.from_dict(WeeklySummary).to_html() + FilterdDataHtml + RowDataHtml +"</body></html>"


            MR.SendMail(MailList = self.MailList , Subject='AM lab Utilization for %s - %s'%(StartTime.strftime('%m-%d') , EndTime.strftime('%m-%d')) , HtmlStr=HtmlStr)


        except Exception as err:
            print str(err)
      
            pass

if __name__ == '__main__':
  kpiWeekly = KPIWeekly()
  kpiWeekly.Exec()


