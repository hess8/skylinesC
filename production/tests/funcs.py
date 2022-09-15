from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

def emailMessage(subject, html, senderEmail,receiverEmail):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = senderEmail
    message["To"] = receiverEmail
    message.attach(MIMEText(html,"html"))
    with smtplib.SMTP('localhost') as server:
        server.sendmail(senderEmail,receiverEmail,message.as_string())
