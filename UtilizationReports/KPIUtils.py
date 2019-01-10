##############################################################################################################################################################################################
##########################################       YairB
##############################################################################################################################################################################################



JHilidays={}
JHilidays["01.03.2018"]="Purim"
JHilidays["31.03.2018"]="Pesach"
JHilidays["06.04.2018"]="Pesach"
JHilidays["20.04.2018"]="IID"
JHilidays["20.05.2018"]="Shavuot"
JHilidays["10.09.2018"]="Rosh"
JHilidays["11.09.2018"]="Rosh"
JHilidays["19.09.2018"]="YK"
JHilidays["24.09.2018"]="Sukot"
JHilidays["01.10.2018"]="Sukot"
JHilidays["21.03.2019"]="Purim"
JHilidays["09.04.2019"]="Israeli legislative election"
JHilidays["20.04.2019"]="Pesach"
JHilidays["26.04.2019"]="Pesach"
JHilidays["10.05.2019"]="IID"
JHilidays["09.06.2019"]="Shavuot"
JHilidays["30.09.2019"]="Rosh"
JHilidays["01.10.2019"]="Rosh"
JHilidays["09.10.2019"]="YK"
JHilidays["14.10.2019"]="Sukot"
JHilidays["21.10.2019"]="Sukot"
JHilidays["10.03.2020"]="Purim"
JHilidays["09.04.2020"]="Pesach"
JHilidays["15.04.2020"]="Pesach"
JHilidays["29.04.2020"]="IID"
JHilidays["29.05.2020"]="Shavuot"
JHilidays["19.09.2020"]="Rosh"
JHilidays["20.09.2020"]="Rosh"
JHilidays["28.09.2020"]="YK"
JHilidays["03.10.2020"]="Sukot"
JHilidays["10.10.2020"]="Sukot"

PRINTERS = {'Carmel 1':33 , 'Carmel 2':29 , 'Carmel 3':31 , 'Carmel 8':44 , 'Carmel 16':45 ,'Pre Alpha':34 , 'Carmel 17':50 , 'Carmel 20':51 , 'carmel 9' : 47 , 'MJ 1' : 36}

import datetime
import mysql.connector
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

class CKPIUtils():



    def __init__(self):
        self.StandartWorkingHours=24
        self.BeforeWeekendWorkingHours=14 #00:00 - 14:00
        self.AfterWeekendWorkingHours=15  #09:00 - 24:00




    def CalcTotalWorkingHours(self ,StartTime , EndTime):
        Today = StartTime
        TotalWorkingHours=0
        while Today <  EndTime : 
            tomorrow = Today + datetime.timedelta(days=1)
            yesterday = Today - datetime.timedelta(days=1)
            if Today.strftime("%d.%m.%Y") in JHilidays.keys():
                pass #No working hours on Holidays
            elif tomorrow.strftime("%d.%m.%Y") in JHilidays.keys():
                TotalWorkingHours+=self.BeforeWeekendWorkingHours
            elif yesterday.strftime("%d.%m.%Y") in JHilidays.keys():
                TotalWorkingHours+=self.AfterWeekendWorkingHours
            elif Today.weekday() == 6: #Sunday  
                TotalWorkingHours+=self.AfterWeekendWorkingHours
            elif Today.weekday() == 4: #Friday  
                TotalWorkingHours+=self.BeforeWeekendWorkingHours
            else:
                TotalWorkingHours+=self.StandartWorkingHours
            Today = tomorrow
        print TotalWorkingHours
        return TotalWorkingHours

    def GetUtilizationInfo(self , StartTime , EndTime , ReturnRowEvents = False):
        SummaryDict={"Machine Name":[],"Working Hours":[],"Total Hours":[],  "Utilization (precent)":[] }
        if ReturnRowEvents:
            SummaryDict['Raw Data']=[]
            SummaryDict['Filterd Data']=[]
        try:
            cnx = mysql.connector.connect(host='SWTEAM', database='XJetDB', user='ViewerUser', password='ViewerUser')
            cursor = cnx.cursor()

            TotalWorkingHours = self.CalcTotalWorkingHours(StartTime , EndTime)
            for pp in PRINTERS:
                PrinterId = PRINTERS[pp]
                query = 'SELECT  EventId,EventTime,EventTypeId from  PrintersEvents where '
                query+= 'EventTime > \'%s\' and EventTime < \'%s\' and PrinterId=%d and (EventTypeId=10 or EventTypeId=11)'%(StartTime,EndTime,PrinterId)
                df = pd.read_sql(query ,con=cnx)

                ExpectStart = True
                StartCandidate = None
                StartEventId   = None
                EndEventId   = None

                StartList=[]
                StopList=[]
                JobIds=[]
                LastPrintedSliceList=[] 
                RowEvents={10:[] , 11:[]}



                if df.shape[0] > 0 and df['EventTypeId'][0] == 11:
                    StartCandidate = StartTime; 
                    StartEventId=-1
                    ExpectStart = False
                for i in range(df.shape[0]):
                    RowEvents[df['EventTypeId'][i]].append(str(df['EventTime'][i]))
                    if ExpectStart and df['EventTypeId'][i] == 10:
                        StartCandidate = df['EventTime'][i]
                        StartEventId = df['EventId'][i]
                        ExpectStart = False
                        continue
                    if ExpectStart and df['EventTypeId'][i] == 11:
                        continue
                    if not ExpectStart and df['EventTypeId'][i] == 10:
                        StartCandidate = df['EventTime'][i]
                        StartEventId = df['EventId'][i]
                        continue
                    if not ExpectStart and df['EventTypeId'][i] == 11:
                        StartList.append(StartCandidate)
                        StopList.append(df['EventTime'][i])
                        StartCandidate = None
                        ExpectStart = True

                        if ReturnRowEvents:
                            query = 'SELECT JobId from EventJobId where EventId=%d'%StartEventId
                            cursor.execute(query)
                            AllRes = cursor.fetchall()
                            if len(AllRes)>0:  
                                JobIds.append(AllRes[0][0])
                            else:
                                JobIds.append('NONE');

                            query = 'SELECT LastPrintedSlice from JobEndedInfo where EventId=%d'%df['EventId'][i]
                            cursor.execute(query)
                            AllRes = cursor.fetchall()
                            if len(AllRes)>0:  
                                LastPrintedSliceList.append(AllRes[0][0])
                            else:
                                LastPrintedSliceList.append('NONE')




                if StartCandidate != None:
                    StartList.append(StartCandidate)
                    StopList.append(EndTime)
                    JobIds.append('NONE');
                    LastPrintedSliceList.append('NONE')
                dff = pd.DataFrame.from_dict({'Start':StartList , 'End':StopList})
                dff['gap']=dff['End']-dff['Start']
                if ReturnRowEvents:
                   dff['Job Id']=JobIds
                   dff['End Slice Id']=LastPrintedSliceList
                   SummaryDict["Filterd Data"].append(dff)
                   SummaryDict["Raw Data"].append(RowEvents)

                GapSum = pd.Timedelta(dff['gap'].sum())
                SummaryDict["Machine Name"].append(pp)
                SummaryDict["Working Hours"].append(GapSum.total_seconds()//3600)
                SummaryDict["Total Hours"].append(TotalWorkingHours)
                SummaryDict["Utilization (precent)"].append(pd.Timedelta(dff['gap'].sum()) / pd.Timedelta('%d hours'% TotalWorkingHours)*100)
                
            cursor.close()
            cnx.close()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except Exception as e:
            print e
        except :
            print "Unexpected error:", sys.exc_info()[0]

        return SummaryDict

    def SendMail(self , MailList , Subject , HtmlStr ,CsvStr=None , CsvFileName=None):
        msg = MIMEMultipart()
        msg['Subject'] = Subject

        s = smtplib.SMTP('pod51014.outlook.com',587)
        s.starttls()
        s.login('bugs@xjet3d.com', 'Bug12345')

        msg['To'] = ','.join(MailList)
        part = MIMEText(HtmlStr, 'html')
        msg.attach(part)
        if CsvStr != None and CsvFileName != None:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(CsvStr)
            part.add_header('Content-Disposition', 'attachment; filename=%s'%CsvFileName)
            msg.attach(part)
        s.sendmail('bugs@xjet3d.com', MailList , msg.as_string())
        s.quit()



