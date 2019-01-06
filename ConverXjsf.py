#!/usr/bin/python

# Turn the last job sent to the BuildEngine into an XJSF file.
import sqlite3

#db = sqlite3.connect('/work/MetalJet/XjetApps/MetalJet/Apps/Project/qt/TestData/RegressionTests/BuildEngineTests/BuildEngine.db')
db = sqlite3.connect('/mnt/xjetsrv/public/users/yAIR/BuildEngine.db')


# Create an xjsf file
for i in range(1,7):
    row = db.execute('select JsonCommand,TrayData from Tray where SlicesGroupId=%d;'%i).fetchone()
    fileName="/tmp/Tray_%s.fabbproject.xjsf"%i
    fh=open(fileName,'wb')

    JsonString = row[0].encode('ascii','ignore')
    fh.write(JsonString[1:-1])
    fh.write(row[1][0:])
    fh.close()

print'ok' 
