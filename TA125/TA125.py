import pandas as pd

# Read the CSV into a pandas data frame (df)
#   With a df you can do many things
#   most important: visualize data with Seaborn

MONTH_NUM = 240 
TA125Csv = 'Data_20181030.csv'
FIBI1Csv = 'FibiSave20181204502964.csv'
FIBI2Csv = 'FibiSave201812045120631.csv'

df125 = pd.read_csv(TA125Csv, delimiter=',')
dffibi1 = pd.read_csv(FIBI1Csv, delimiter=',')
dffibi2 = pd.read_csv(FIBI2Csv, delimiter=',')

AllTA125Tick = [df125.loc[i,'Security Number'] for i in range(len(df125))]
AllFIBI1Tick = [int(dffibi1.loc[i,'TICNUM']) for i in range(1,len(dffibi1)) ]
AllFIBI2Tick = [int(dffibi2.loc[i,'TICNUM']) for i in range(1,len(dffibi2)) ]
'''
for i in range(len(dffibi1)):
  print dffibi1.loc[i,'TICNUM']
'''

SoFar =  (set(AllTA125Tick) - set(AllFIBI1Tick)) - set(AllFIBI2Tick)
for i in range(len(df125)):
  if df125.loc[i,'Security Number'] in SoFar : 
    print df125.loc[i,'Name'],':',df125.loc[i,'Weight']," ",df125.loc[i,'Security Number']
#print (AllFIBI1Tick) 
#print (AllFIBI2Tick)
'''
  ValueOnEnd = df.loc[MONTH_NUM+i , 'Close'] * MONTH_NUM
  TotalInvestment = sum(df['Close'][i:MONTH_NUM+i])
  Precent = ((ValueOnEnd-TotalInvestment)*100)/TotalInvestment
  TotalPrecent += Precent
  print df['Date'][i]   ,':     ',   Precent, '%', 'Runnung avg' , TotalPrecent/(i+1) , '%'
'''
