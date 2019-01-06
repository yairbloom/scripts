import csv
file1='/home/yair/Downloads/Data_20181030.csv'
filefibi1='/home/yair/Downloads/FibiSave20181025534250.csv'
filefibi2='/home/yair/Downloads/FibiSave201810254326630.csv'
with open(file1, mode='r') as infile:
    reader = csv.reader(infile)
    '''
    for row in reader:
        print row
    '''
    #aa = [row[2]  for row in reader if len(row)>2]
    aa = [row[2]  for row in reader[:4] ]
    print len(aa)
