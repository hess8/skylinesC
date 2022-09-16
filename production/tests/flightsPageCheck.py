import smtplib
import requests
from time import sleep
from datetime import datetime
from funcs import emailMessage, turns

senderEmail = 'skylinesC@soardata.org'
receiverEmail = 'bret.hess@gmail.com'
looptime = 60 #sec
alerttime = 300
print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"), end='\r')
while True:
    try:
        response = requests.get('https://skylinescondor.com/api/flights/all?page=1',timeout=2)
        jsonr = response.json()
        if jsonr['count']>0:
            turns(looptime,'')
            continue
        else:
            subject = 'Zero skylinesC flights count'
            emailMessage(subject, '', senderEmail, receiverEmail)
            turns(alerttime, 'zero count')
    except:
        subject = 'SkylinesC flights page timeout/error'
        emailMessage(subject, '', senderEmail, receiverEmail)
        turns(alerttime,'timeout/error')





