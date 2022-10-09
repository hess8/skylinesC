from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import timedelta,datetime
from time import sleep

def emailMessage(subject, html, senderEmail,receiverEmail):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = senderEmail
    message["To"] = receiverEmail
    message.attach(MIMEText(html,"html"))
    with smtplib.SMTP('localhost') as server:
        server.sendmail(senderEmail,receiverEmail,message.as_string())

def turns(delta, str):
    blank = '                                         '  ##
    start = datetime.now()
    while datetime.now() < start + timedelta(seconds=delta):
        print(blank, end='\r')
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"), '-', str, end='\r')
        sleep(0.5)
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"), '\\', str, end='\r')
        sleep(0.5)
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"), '|', str, end='\r')
        sleep(0.5)
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"), '/', str, end='\r')
        sleep(0.5)

