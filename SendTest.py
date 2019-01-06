import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

fp=open('/tmp/aaa.html', 'rb')


aa=fp.read()
msg = MIMEText(aa ,'html')

fp.close()
msg['Subject'] = "AAAA BBBBB"
 
  
msg['From'] = 'bugs@xjet3d.com'
msg['To'] = 'Yair.Bloom@xjet3d.com'

# Send the message via our own SMTP server.
s = smtplib.SMTP('pod51014.outlook.com',587)
s.starttls()
s.login('bugs@xjet3d.com', 'Bug12345')
s.sendmail('bugs@xjet3d.com', 'Yair.Bloom@xjet3d.com', msg.as_string())
s.quit()
 
