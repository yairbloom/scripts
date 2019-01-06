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

PRINTERS = {'Alpha':33 , 'Alpha2':29 , 'Alpha3':31 , 'Alpha8':44 , 'CARMEL-16':45 ,'PreAlpha':34}

import datetime
import mysql.connector
import pandas as pd

class CMonthlyReport():



    def __init__(self , Month , Year):
        self.Month = Month
        self.Year = Year
        self.StandartWorkingHours=24
        self.BeforeWeekendWorkingHours=16
        self.AfterWeekendWorkingHours=16
        self.CalcTotalWorkingHours()




    def CalcTotalWorkingHours(self ):
        Today = datetime.datetime(self.Year, self.Month, 1)
        TotalWorkingHours=0
        while Today.month == self.Month : 
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
        return TotalWorkingHours

    def FetchDataFromMachineDB(self):
        SummaryDict={"Machine Name":[],"Working Hours":[],"Total Hours":[],  "Utilization (precent)":[]}
        try:
            StartDay = datetime.datetime(self.Year, self.Month, 1)
            EndDay =   datetime.datetime(self.Year+ self.Month/12 , self.Month%12+1, 1)
            cnx = mysql.connector.connect(host='SWTEAM', database='XJetDB', user='ViewerUser', password='ViewerUser')
            cursor = cnx.cursor()

            for pp in PRINTERS:
                PrinterId = PRINTERS[pp]
                query = 'SELECT  EventTime,EventTypeId from  PrintersEvents where EventTime > \'%s\' and EventTime < \'%s\' and PrinterId=%d and (EventTypeId=10 or EventTypeId=11)'%(StartDay,EndDay,PrinterId)
                df = pd.read_sql(query ,con=cnx)

                ExpectStart = True
                StartCandidate = None
                StartList=[]
                StopList=[]
                RowEvents={10:[] , 11:[]}



                if df.shape[0] > 0 and df['EventTypeId'][0] == 11:
                    StartCandidate = StartDay; 
                    ExpectStart = False
                for i in range(df.shape[0]):
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
                if StartCandidate != None:
                    StartList.append(StartCandidate)
                    StopList.append(EndDay)
                     
                dff = pd.DataFrame.from_dict({'Start':StartList , 'End':StopList})
                dff['gap']=dff['End']-dff['Start']

                TotalWorkingHours = self.CalcTotalWorkingHours()
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

