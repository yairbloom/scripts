import socket
import subprocess
import json
import struct
import sqlite3
import os.path 
import sys
from PIL import Image

Image.MAX_IMAGE_PIXELS = 400000000

MJ_MSG_PRINTER_ID = u"PrinterId"
MJ_MSG_JOB_ID = u"JobId"
MJ_MSG_JOB_NAME = u"JobName"
MJ_MSG_CREATION_TIME = u"SubmittedTime"
MJ_MSG_START_TIME = u"StartTime"
MJ_MSG_END_TIME = u"EndTime"
MJ_MSG_JOB_DATA = u"JobData"
MJ_MSG_TOTAL_SLICES = u"TotalSlices"
MJ_MSG_BE_HOST_NAME = u"BuildEngineHostName"
MJ_MSG_BE_SLICES_DUMP_DIR = u"BuildEngineSlicesDumpDir"

class CReporterServer():
    def __init__(self):
        self.LISTENING_PORT = 5555
        self.ThumbnailSize = 750, 250
        self.LastJobId = -1
        self.ExportModelFolder = ''
        self.ExportSupportFolder = ''
        self.ExportThumbnailModelFolder = ''
        self.ExportThumbnailSupportFolder = ''

        currentDir = os.path.dirname(os.path.realpath(__file__))
        

        if sys.platform not in ['win32','nt']:
            self.BuildEngineDbFile = os.path.join(currentDir , '..' , 'BinLinux' ,'BuildEngine.db')
        else: # windows
            self.BuildEngineDbFile = os.path.join(currentDir , '..' , 'BinWin64' ,'BuildEngine.db')


    def GenrateThumbnail(self):
        if not os.path.isdir(self.ExportModelFolder) and not os.path.isdir(self.ExportSupportFolder):
            return False
        Ret = False
        if not os.path.isdir(self.ExportThumbnailModelFolder) and os.path.isdir(self.ExportModelFolder):
            os.makedirs(self.ExportThumbnailModelFolder)
        if not os.path.isdir(self.ExportThumbnailSupportFolder) and os.path.isdir(self.ExportSupportFolder):
            os.makedirs(self.ExportThumbnailSupportFolder)

        ExportsObj=[{'ExportFolder': self.ExportModelFolder , 'ThumbnailFolder': self.ExportThumbnailModelFolder}] 
        ExportsObj.append({'ExportFolder': self.ExportSupportFolder,'ThumbnailFolder': self.ExportThumbnailSupportFolder})
        for Obj in ExportsObj : 
            for f in sorted(os.listdir(Obj['ExportFolder'])) :
                if not f.endswith('.png'):
                    continue
                SourceFilePath = os.path.join(Obj['ExportFolder'] , f)
                ThumbnailFileName = os.path.splitext(f)[0] + ".thumbnail.png"             
                ThumbnailFilePath = os.path.join(Obj['ThumbnailFolder'] , ThumbnailFileName)
                if os.path.isfile(ThumbnailFilePath):
                    continue
                try :
                    im = Image.open(SourceFilePath)
                    im.thumbnail(self.ThumbnailSize, Image.ANTIALIAS)
                    im.save(ThumbnailFilePath, "png")
                    Ret = True
                    break;
                except IOError as e:
                    print e
        return Ret


    def listen(self):
        tlcall= 'netstat -ano | findstr :'%(self.LISTENING_PORT)
        tlproc = subprocess.Popen(tlcall, shell=True, stdout=subprocess.PIPE)
        tlout = tlproc.communicate()[0].strip().split()
        if len(tlout) > 1 :
            print "Port %d already bound"
            sys.exit()

        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind(('0.0.0.0', self.LISTENING_PORT))
        connection.listen(4)
        while True:
            try :
                current_connection, address = connection.accept()
                data = current_connection.recv(256)
                RequestJsonObj = json.loads(data)
                if MJ_MSG_PRINTER_ID in RequestJsonObj and MJ_MSG_JOB_ID in RequestJsonObj :
                    self.LastJobId = RequestJsonObj[MJ_MSG_JOB_ID]
                    conn = sqlite3.connect(self.BuildEngineDbFile)
                    cursor = conn.cursor()
                    SqlStr='SELECT JobName,SlicesGroupId,CreationTime,StartTime,EndedTime from JobsPrinters where JobId=%d'%self.LastJobId
                    cursor.execute(SqlStr)
                    row = cursor.fetchone()
                    if row == None:
                        conn.close()
                        continue
               
                    JsonDict = {MJ_MSG_JOB_NAME : row[0] , MJ_MSG_CREATION_TIME : row[2] , MJ_MSG_START_TIME : row[3] , MJ_MSG_END_TIME : row[4]}
                    SlicesGroupId = row[1]
                    SqlStr='SELECT JsonCommand from Tray where SlicesGroupId=%d'%SlicesGroupId
                    cursor.execute(SqlStr)
                    row = cursor.fetchone()
                    if row == None:
                        conn.close()
                        continue
                    
                    JsonCommand = json.loads(row[0])
                    JsonDict[MJ_MSG_JOB_DATA] = JsonCommand[MJ_MSG_JOB_DATA]

                    SqlStr='SELECT TotalSlices,BuildEngineHostName,BuildEngineSlicesDumpDir from SlicesGroupParams  where SlicesGroupId=%d'%SlicesGroupId
                    cursor.execute(SqlStr)
                    row = cursor.fetchone()
                    if row == None:
                        conn.close()
                        continue
              
                    JsonDict[MJ_MSG_TOTAL_SLICES] = row[0]
                    JsonDict[MJ_MSG_BE_HOST_NAME]        = row[1]
                    JsonDict[MJ_MSG_BE_SLICES_DUMP_DIR]        = os.path.basename(row[2])
                    print JsonDict[MJ_MSG_BE_SLICES_DUMP_DIR] 
                    self.ExportModelFolder = os.path.join(row[2] , 'Model')
                    self.ExportSupportFolder = os.path.join(row[2] , 'Support')
                    self.ExportThumbnailModelFolder =  os.path.join(row[2] , 'ThumbnailModel')
                    self.ExportThumbnailSupportFolder = os.path.join(row[2] , 'ThumbnailSupport') 



                    JsonResponse = json.dumps(JsonDict , sort_keys=True, indent=4, separators=(',', ': '))

                    strlen = len(JsonResponse)
                    msgSize = struct.pack("I", strlen)
                    current_connection.send(msgSize)
                    current_connection.send(JsonResponse)
                    current_connection.close()
                    conn.close()
                    
                    if self.GenrateThumbnail():
                        connection.settimeout(1)
            except socket.timeout:
                if not self.GenrateThumbnail():
                    connection.settimeout(None)
                print 'socket.timeout'
            except KeyboardInterrupt:
                conn.close()
                break;
            except Exception as e:
                print e
                conn.close()
                continue
            except:
                print 'undefine error'
                conn.close()
                continue
        




if __name__ == "__main__":
    ReporterServer = CReporterServer()
    try:
        ReporterServer.listen()
    except KeyboardInterrupt:
        pass
