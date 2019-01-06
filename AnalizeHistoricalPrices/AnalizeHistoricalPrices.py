import pandas as pd

# Read the CSV into a pandas data frame (df)
#   With a df you can do many things
#   most important: visualize data with Seaborn

MONTH_NUM = 240 
HistoricalRateFileName = 'TA100.csv'
#HistoricalRateFileName = 'GSPC.csv'
#HistoricalRateFileName = 'Nikkei.csv'
df = pd.read_csv(HistoricalRateFileName, delimiter=',')

TotalPrecent = 0

for i in range(len(df)-MONTH_NUM):
  print i
  ValueOnEnd = df.loc[MONTH_NUM+i , 'Close'] * MONTH_NUM
  TotalInvestment = sum(df['Close'][i:MONTH_NUM+i])
  Precent = ((ValueOnEnd-TotalInvestment)*100)/TotalInvestment
  TotalPrecent += Precent
  print df['Date'][i]   ,':     ',   Precent, '%', 'Runnung avg' , TotalPrecent/(i+1) , '%'

