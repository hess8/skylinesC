import smtplib
import requests
from time import sleep
from funcs import emailMessage

senderEmail = 'skylinesC@soardata.org'
receiverEmail = 'bret.hess@gmail.com'
looptime = 60 #sec
alerttime = 300
subject = 'SkylinesCondor flights page down'
while True:
    try:
        response = requests.get('https://skylinescondor.com/api/flights/',timeout=2)
        jsonr = response.json()
    except:
        print('Timeout')
        emailMessage(subject, '', senderEmail, receiverEmail)
        sleep(alerttime)
    sleep(looptime)





