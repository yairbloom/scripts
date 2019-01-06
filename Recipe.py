import mysql.connector
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import sys
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

'''
+-----------+-------------+
| PrinterId | PrinterName |
+-----------+-------------+
|        29 | Alpha2      |
|        31 | Alpha3      |
|        33 | Alpha       |
|        34 | PreAlpha    |
|        35 | MiniJet2    |
|        36 | MINIJET1    |
|        37 | swteam      |
|        38 | HYDRA       |
|        39 | MiniJet3    |
|        40 | MiniJet5    |
|        41 | MINIJET4    |
|        42 | Alpha4      |
|        43 | Alpha7      |
|        44 | Alpha8      |
|        45 | CARMEL-16   |
+-----------+-------------+


'''




PRINTERS = {'Alpha3':31 , 'Alpha8':44 }

class AmMachineUtilization:
    def __init__(self):
        self.TotalHoursTime = 90*24 #Sun 8:00 - Fri 16:00 
        self.MailList=['yair.bloom@xjet3d.com','omer.dolev@xjet3d.com']
 
    def Exec(self):
        try:
            StartTime = datetime.now()-timedelta(hours=self.TotalHoursTime)
            EndTime = datetime.now()
            MsgBudy=self.GetDataFromMachineDb(StartTime , EndTime)
            msg = MIMEMultipart()
            msg['Subject'] = "Measurement for %s - %s"%(StartTime.strftime('%m-%d') , EndTime.strftime('%m-%d'))

            s = smtplib.SMTP('pod51014.outlook.com',587)
            s.starttls()
            s.login('bugs@xjet3d.com', 'Bug12345')


            SepStr=''
            ToList=''
            for email in self.MailList:
                ToList = ToList+SepStr+email
                SepStr = ','
            msg['To'] = ToList
            part = MIMEText(MsgBudy, 'html')
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

            TheHtml = "<html><head></head><body><h3>Summary from %s to %s</h3>"%(StartTime.strftime('%Y-%m-%d %H:%M:%S') ,  EndTime.strftime('%Y-%m-%d %H:%M:%S'))
            FilterdDataHtml='<h3>Filtered start/stop time events</h3>'
            for pp in PRINTERS:
                PrinterId = PRINTERS[pp]
                query = 'SELECT  EventId,EventTime,EventTypeId from  PrintersEvents where EventTime > (NOW() - INTERVAL %d HOUR) and PrinterId=%d and (EventTypeId=10 or EventTypeId=11)'%(self.TotalHoursTime,PrinterId)
                df = pd.read_sql(query ,con=cnx)

                ExpectStart = True
                StartCandidate = None
                StartEventId   = None
                EndEventId   = None
                StartList=[]
                StopList=[]
                JobIds=[]
                PalletHeights=[] 
                LastPrintedSliceList=[] 
                RowEvents={10:[] , 11:[]}



                for i in range(df.shape[0]):
                  try:
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

                        query = 'SELECT RecipeInfo from JobsRecipeInfo where EventId=%d'%StartEventId
                        cursor.execute(query)
                        AllRes = cursor.fetchall()
                        if len(AllRes)>0:  
                            try:
                                RstrSplit=AllRes[0][0].split('{')
                                Rstr='{'+(RstrSplit[1]).replace('\\','')
                                RecipeInfo=json.loads(Rstr)
                                PalletHeights.append(RecipeInfo['PalletHeightTable'])
                            except:
                                PalletHeights.append('NONE');
                        else:
                            PalletHeights.append('NONE');
                            
                  except Exception as e:
                    print e
                    print df['EventTypeId'][i]


                pd.set_option('display.max_colwidth', -1)
                dff = pd.DataFrame.from_dict({'Start':StartList , 'End':StopList , 'Job Id':JobIds , 'Slice Id':LastPrintedSliceList,'Pallet Heights':PalletHeights})
                if len(df) == 0:
                   continue
                FilterdDataHtml+= '<br><br>'
                FilterdDataHtml+= 'Machine Name:\%s<br>'%(pp)
                FilterdDataHtml+= '%s'%(dff[['Start','End','Job Id','Slice Id','Pallet Heights']]).to_html()

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
        TheHtml+=FilterdDataHtml +"</body></html>"
        return TheHtml


if __name__ == '__main__':
  amMachineUtilization = AmMachineUtilization()
  amMachineUtilization.Exec()


