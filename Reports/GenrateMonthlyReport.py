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
            #encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="Utilization.csv"')
            msg.attach(part)
            s.sendmail('bugs@xjet3d.com', self.MailList , msg.as_string())
            s.quit()

        except Exception as err:
            print str(err)
      
            pass


###########################################################  GetDataFromMachineDb ################################################################################
    def GetDataFromMachineDb(self , StartTime , EndTime): 
        try:
            cnx = mysql.connector.connect(host='SWTEAM', database='XJetDB', user='ViewerUser', password='ViewerUser')
            cursor = cnx.cursor()

            TheHtml = "<html><head></head><body><h3>Machines Utilization Summary from %s to %s</h3>"%(StartTime.strftime('%Y-%m-%d %H:%M:%S') ,  EndTime.strftime('%Y-%m-%d %H:%M:%S'))
            RowDataHtml='<h3>Row start/stop time events</h3>'
            FilterdDataHtml='<h3>Filtered start/stop time events</h3>'
            SummaryDict={"Machine Name":[],"Total Working Time":[],"Utilization (precent)":[]}
            for pp in PRINTERS:
                PrinterId = PRINTERS[pp]
                query = 'SELECT  EventTime,EventTypeId from  PrintersEvents where EventTime > (NOW() - INTERVAL %d HOUR) and PrinterId=%d and (EventTypeId=10 or EventTypeId=11)'%(self.TotalHoursTime,PrinterId)
                df = pd.read_sql(query ,con=cnx)

                ExpectStart = True
                StartCandidate = None
                StartList=[]
                StopList=[]
                RowEvents={10:[] , 11:[]}




                for i in range(df.shape[0]):
                    RowEvents[df['EventTypeId'][i]].append(str(df['EventTime'][i]))
                    if ExpectStart and df['EventTypeId'][i] == 10:
                        StartCandidate = df['EventTime'][i]
                        ExpectStart = False
                        continue
                    if ExpectStart and df['EventTypeId'][i] == 11:
                        continue
                    if not ExpectStart and df['EventTypeId'][i] == 10:
                        StartCandidate = df['EventTime'][i]
                        continue
                    if not ExpectStart and df['EventTypeId'][i] == 11:
                        StartList.append(StartCandidate)
                        StopList.append(df['EventTime'][i])
                        StartCandidate = None
                        ExpectStart = True
                dff = pd.DataFrame.from_dict({'Start':StartList , 'End':StopList})
                dff['gap']=dff['End']-dff['Start']
                SummaryDict["Machine Name"].append(pp)
                SummaryDict["Total Working Time"].append(pd.Timedelta(dff['gap'].sum()))
                SummaryDict["Utilization (precent)"].append(pd.Timedelta(dff['gap'].sum()) / pd.Timedelta('%d hours'% self.TotalHoursTime)*100)
                if len(df) == 0:
                   continue
                FilterdDataHtml+= '<br><br>'
                FilterdDataHtml+= 'Machine Name:\%s<br>'%(pp)
                FilterdDataHtml+= '%s'%(dff[['Start','End','gap']]).to_html()
                RowDataHtml+= '<br><br>'
                RowDataHtml+= 'Machine Name%s<br>'%(pp)
                RowDataHtml+= 'Start time events:%s <br>'%(','.join(RowEvents[10]))
                RowDataHtml+= 'Stop time events:%s <br>'%(','.join(RowEvents[11]))

                '''
                fig, ax = plt.subplots()

                for x_1 , x_2 in zip(dff['Start'].values ,dff['End'].values):
                    ax.add_patch(plt.Rectangle((x_1,0),x_2-x_1,0.99))

                ax.autoscale()
                ax.set_ylim(0,1)
                plt.show()
                '''

            cursor.close()
            cnx.close()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except Exception as e:
            print e
        except :
            print "Unexpected error:", sys.exc_info()[0]
        TheHtml+=pd.DataFrame.from_dict(SummaryDict).to_html() + FilterdDataHtml + RowDataHtml +"</body></html>"
        return TheHtml


if __name__ == '__main__':
  amMachineUtilization = AmMachineUtilization()
  amMachineUtilization.Exec()


