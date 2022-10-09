import smtplib
import requests
from time import sleep
from datetime import datetime
from funcs import emailMessage, turns
'''Run with **python3** on deSoto U18'''
page = 'statistics'
# page = 'clubs'
# page = 'flights/all?page=1'
base = 'https://skylinescondor.com/api'
senderEmail = 'skylinesC@soardata.org'
receiverEmail = 'bret.hess@gmail.com'
looptime = 60 #sec
alerttime = 300
print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"), end='\r')
while True:
    try:
        response = requests.get('{}/{}'.format(base,page),timeout=2)
        jsonr = response.json()
        if len(jsonr) > 0:
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





