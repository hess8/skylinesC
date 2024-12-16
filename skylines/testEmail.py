# Import smtplib for the actual sending function
import smtplib
from email.mime.text import MIMEText

sender = 'skylinescondor@soardata.org'
recipient = 'bret.hess@gmail.com'
msg = MIMEText('Message here')
msg['Subject'] = 'abc'
msg['From'] = sender
msg['To'] = recipient
s = smtplib.SMTP('localhost')
s.sendmail(sender, [recipient], msg.as_string())
s.quit()
print 'Done'
