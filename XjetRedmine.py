import redmine

import datetime


redmine=redmine.Redmine('http://172.16.10.84/',username='GeneralOperator',password='1234',version='2.5.0')
projects = redmine.project.all()
MachineLogsDBNameToIdentifier= dict((i.name,i.identifier) for i in projects if hasattr(i,'parent') and i.parent.name == 'Machine logs')

trackers = redmine.tracker.all()
TrackersIdx=dict((tracker.name,tracker.id) for tracker in trackers)
print  MachineLogsDBNameToIdentifier.keys()
for p in MachineLogsDBNameToIdentifier.keys(): 
    try :
        zzz = redmine.issue.filter(project_id=MachineLogsDBNameToIdentifier[p] , subproject_id='!*',tracker_id=TrackersIdx['Application start'],created_on='><2013-01-01|2018-11-01')
        print zzz
        for i in zzz:
            print p,': ',i.id ,' ' ,i.created_on
            try :
                print redmine.issue.delete(i.id)
            except Exception as e:
                print str(e)
            except:
                print 'Unknown error' 
    except Exception as e:
        print p, ' ' ,str(e)
        continue
'''
aaa = RU.GetJobsList('MiniJetTest')

bbb = [x for x in aaa if x["created_on"] < datetime.datetime(2018,1,1,0,0,0)]

print bbb[0]
'''
