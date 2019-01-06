import mysql.connector

############################################################################# INPUT ###################################################################################################################

PrinterId=33 
JobId=190
#select PrinterId,PrinterIdentifer from PrintersTables; => 33=ALPHA,31=ALPHA3,42=ALPHA4,43=Alpha7,38=HYDRA,36=MINIJET1,35=MiniJet2,39=MiniJet3,41=MINIJET4,40=MiniJet5,34=PreAlpha,29=Strobe1,37=swteam

host='swteam'
user='YaronIdeses'
password ='Yaron123'
database='XJetDB'

############################################################################# OUPUT ###################################################################################################################


def DoReport(cursor):
  StartEventId=-1
  print "\n\n\n\t\t\t\t\t\t\t\t\t\t\t Job %d  progress: \n" % (JobId)
  print "\t\t\t\t\t\t\t\t\t ******************************************* \n\n"
  query = 'select A.EventTime,A.EventId,A.EventTypeId from PrintersEvents as A,EventJobId as B where B.JobId = %d ' % (JobId)
  query = ' %s and (A.EventTypeId=10 or A.EventTypeId=11) and A.EventId=B.EventId and A.PrinterId=%d order by A.EventTime limit 10;' % (query , PrinterId)
  cursor.execute(query)
  AllRes = cursor.fetchall()
  for OneRes in AllRes:
    if  OneRes[2]==11:
      query = 'select JobEndedSuccessfully,LastPrintedSlice from JobEndedInfo where EventId=%d' % (OneRes[1])
      cursor.execute(query)
      JEAllRes = cursor.fetchall()
      if len(JEAllRes) > 0:
        if JEAllRes[0][0]==0:
          print OneRes[0],"Job ",JobId ," stoped  at layer ",JEAllRes[0][1]
        else:
          print OneRes[0],"Job " , JobId , " Ended Successfully at layer ",JEAllRes[0][1]
    if OneRes[2]==10:
      print OneRes[0]," Job ",JobId," Started"
      StartEventId=OneRes[1]
  query = 'select RecipeInfo from JobsRecipeInfo  where EventId=%d' % (StartEventId)   
  cursor.execute(query)
  AllRes = cursor.fetchall()
  for OneRes in AllRes:
    print "\n\n\n\t\t\t\t\t\t\t\t\t\t\t Job %d  Recipe: \n" % (JobId)
    print "\t\t\t\t\t\t\t\t\t ******************************************* \n\n"
    print OneRes[0]
#----------------------------------------------------------------------------- main -----------------------------------------------------------------
if __name__ == '__main__':
  cnx = mysql.connector.connect(user=user,password =password,host=host,database=database)
  cursor = cnx.cursor()
  DoReport(cursor)
  cnx.commit()
  cursor.close()
  cnx.close()
