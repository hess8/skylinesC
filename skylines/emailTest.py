# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
# from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.
# fp = open(textfile, 'rb')
# # Create a text/plain message
# msg = MIMEText(fp.read())
# fp.close()

msg = MIMEMultipart()

sender = 'skylinescondor@soardata.org'
recipient = 'bret.hess@gmail.com'

msg['Subject'] = 'abc'
msg['From'] = sender
msg['To'] = recipient

# Send the message via our own SMTP server, but don't include the
# envelope header.

s = smtplib.SMTP()
s.connect('localhost', '587')



# s = smtplib.SMTP('localhost')
s.sendmail(sender, [recipient], msg.as_string())
s.quit()
s.quit()
