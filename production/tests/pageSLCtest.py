import smtplib
import requests
from time import sleep
from datetime import datetime
from funcs import emailMessage, turns

'''Run with **python3** on nginx server U18

now using cron.d/ file:

# m h dom mon dow user  command
* * * * * bret python3 /home/bret/production/tests/pageSLCtest.py --noloop # run every minute
# Can't end command line without line break


'''
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--noloop", help="stops loop",action="store_true")
args = parser.parse_args()
noloop = args.noloop
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
            if noloop:
                break
            turns(looptime,'')
            # if loop:
            #     continue
        else:
            subject = 'Zero skylinesC flights count'
            emailMessage(subject, '', senderEmail, receiverEmail)
            if noloop:
                break
            turns(alerttime, 'zero count')
    except:
        subject = 'SkylinesC flights page timeout/error'
        emailMessage(subject, '', senderEmail, receiverEmail)
        if noloop:
            break
        turns(alerttime,'timeout/error')






