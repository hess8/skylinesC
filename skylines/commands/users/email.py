from __future__ import absolute_import, print_function

from flask_script import Command, Option

import os,sys
import smtplib
from email.mime.text import MIMEText
from flask import current_app

from skylines.database import db
from skylines.model import User
from skylines.common import readfileNoStrip


class Email(Command):
    """ Send email to all users """

    option_list = (
        Option("path", help="path to a text file with the content of the email"),
        Option("to", help="can be 'admin' (goes to ) or 'all'")
    )

    def sendEmail(self, user, sender, recipient, title, text):
        print('Sending email to {} (ID: {})...'.format(user.name, user.id))
        try:
            body = 'Hi {},\n'.format(user.name.split(' ')[0])
            body += text
            msg = MIMEText(body)
            msg["Subject"] = title
            msg["From"] = sender
            s = smtplib.SMTP('localhost')
            s.sendmail(sender, [recipient], msg.as_string())
            s.quit()
        except BaseException as e:
            print("Sending email failed: {}", e)


    def run(self, path, to):

        if to not in ['admin','all']:
            sys.exit('Stop: last option must be "admin" or "all"')
        sender = 'skylinescondor@soardata.org'
        os.chdir('/home/bret/servers/repo-skylinesC/skylinesC')
        lines = readfileNoStrip(path)
        title = lines[0].strip()
        text = ''
        for line in lines[1:]:
            text += line
        text += "\nFor help contact skylinescondor@gmail.com.  Don't reply to this message."
        text += '\n\n--Bret at SkylinesCondor'
        users_query = (
            db.session.query(User).filter(User.email_address != None).order_by(User.id)
        )

        for user in users_query:
            recipient = user.email_address
            if to == 'admin' and user.admin:
                self.sendEmail(user,sender,recipient,title, text)
                break
            elif to == 'all':
                self.sendEmail(user,sender,recipient,title,text)






