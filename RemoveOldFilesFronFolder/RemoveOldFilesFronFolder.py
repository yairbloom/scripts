import os
import time
import shutil

##############################################    input parametes  ##############################################################

FOLDER='/home/yair/Downloads'
NUM_OF_DAYS=180

#################################################################################################################################

current_time = time.time()

for f in os.listdir(FOLDER):
    FileName = os.path.join(FOLDER , f);
    creation_time = os.path.getctime(FileName)
    if (current_time - creation_time) > (24 * 3600 * NUM_OF_DAYS):
        try:
          print('{} removed'.format(FileName))
          shutil.rmtree(FileName, ignore_errors=True, onerror=None)
          os.unlink(FileName)
        except:
          pass
