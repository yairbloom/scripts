import pandas as pd
import csv

fibi1= '/home/yair/scripts/TTT125/FibiSave20181223310326.csv'
fibi2='/home/yair/scripts/TTT125/FibiSave201812225959916.csv'
ta125= '/home/yair/scripts/TTT125/indexcomponents.csv'

#df1 = pd.read_csv(fib1,skiprows = [1])
#df2 = pd.read_csv(fibi2 , skiprows=[1])

#print df2.columns


#df2 = pd.read_csv(fib2)
#df125 = pd.read_csv(ta125)

aaa={}
with open(fibi1, mode='r') as infile:
    reader = csv.reader(infile)
    next(reader, None)
    next(reader, None)
    next(reader, None)
    for row in  reader:
      aaa[int(row[2])] = float(row[13].replace(",", ""))

with open(fibi2, mode='r') as infile:
    reader = csv.reader(infile)
    next(reader, None)
    next(reader, None)
    next(reader, None)
    for row in  reader:
      if int(row[1]) in aaa:
        aaa[int(row[1])] += float(row[13].replace(",", ""))
      else:
        aaa[int(row[1])] = float(row[13].replace(",", ""))

   
with open(ta125, mode='r') as infile:
    reader = csv.reader(infile)
    next(reader, None)
    next(reader, None)
    next(reader, None)
    for row in  reader:
        Ind = int(row[2])
        if Ind in aaa:
          print Ind, ': ' , aaa[Ind]
        else:
          print Ind, ': 0'
