from __future__ import absolute_import, print_function

from flask_script import Command, Option

import os
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
    )

    def run(self, path):
        os.chdir('/home/bret/servers/repo-skylinesC/skylinesC')
        sender = 'skylinescondor@soardata.org'
        lines = readfileNoStrip(path)
        title = lines[0].strip()
        text = ''
        for line in lines[1:]:
            text += line
        text += '\nBret'
        users_query = (
            db.session.query(User).filter(User.email_address != None).order_by(User.id)
        )

        for user in users_query:
            if 'Hess' not in user.name:
                continue ##########test
            print(
                u"Sending email to {} (ID: {})...".format(user.name, user.id).encode(
                    "utf-8"
                )
            )

            try:
                recipient = user.email_address
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
