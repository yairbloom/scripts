#!/usr/bin/python

# A script for getting machine status from the linux command line.

import re
import sys
import time
import json

argp = 1

UnixStyle = False
Filter = None

while len(sys.argv)>argp and sys.argv[argp][0]=='-':
  S_ = sys.argv[argp]
  argp+= 1

  if S_=='-help':
    print '''MachineStatus.py - Show machine status

Options:
    -unix    Show options unix style.
'''

  if S_=='-unix':
    UnixStyle = True
    continue

  sys.stderr.write('Unknown option ' + S_ + '!\n')
  exit(-1)

if argp < len(sys.argv):
  Filter = sys.argv[argp]
  argp+=1
  
sys.path.insert(0,
                '../Lib'
                )
import RemoteClient

HostsToWatch = [
                'mj1',
                'minijet2',
                'minijet3',
                'minijet4',
                'minijet5',
                'prealpha',
                'alpha',
                'alpha2',
                'alpha3',
                'alpha5',
                'strobe1'
  ]

Statuss = []
Errors = []

GetStatusCode = '''
try:
  CurrentSliceId = PrintEngine.PrintPassExecuter.GetCurrentLayersNum()
except:
  CurrentSliceId = -1

CurrentStatus = \
{
    'Online': PrintEngine.PrintFlowManager.IsOnline(),
    'NumSlicesInJob' : PrintEngine.PrintFlowManager.GetNumberOfSlicesInJob(),
    'HasJob' : PrintEngine.PrintFlowManager.HasJob(),
    'SliceId' : CurrentSliceId,
    'ConfigDir' : PrintEngine.Application.ConfigDir,
    'Sha1' : PrintEngine.Application.Build,
    'Version' : PrintEngine.Application.GetVersion(),
    'JobName' : PrintEngine.PrintingPersistDataManager.LastJobName,
}
'''

for Host in HostsToWatch:
  if Filter is not None and Host != Filter:
    continue
  rc = RemoteClient.RemoteClient(Host=Host)
  try:
    rc.EvalPythonString('import PrintEngine;\n'
                        'import json;\n'
                        + GetStatusCode
                        + 'PrintEngine.CurrentStatus = json.dumps(CurrentStatus)',
                        Timeout=1
                        )
  
    res = rc.GetPython('PrintEngine.CurrentStatus')
  except Exception as e:
    Errors += [(Host, str(e))]
    res = '"Error: %s"'%str(e)
  try:
    Statuss += [(Host,json.loads(res))]
  except:
    print res, 'is not parsable for ', Host
    

for Host,Status in Statuss:
  print Host
  if isinstance(Status,unicode) and Status.startswith('Error'):
    print '  '+ Status + '\n'

  else:
    Online = Status['Online']
    ConfigDir = Status['ConfigDir']
    if UnixStyle:
      ConfigDir = re.sub('^([A-Z]):',
                         lambda m: '/mnt/' + Host + '/' + m.group(1).lower(),
                         ConfigDir.replace('\\','/'))
    print '  ConfigDir:    ', ConfigDir
    print '  SHA1:         ', Status['Sha1']
    print '  Version:      ', '.'.join([str(v) for v in Status['Version']])
    print '  Status:       ', ['Offline','Online'][Online]
    if Online:
      print '  JobName:       \"'+Status['JobName']+'\"'
      print '  Slice/Total:  ',str(Status['SliceId'])+'/'+str(Status['NumSlicesInJob'])
    print ''
