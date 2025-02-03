from __future__ import absolute_import, print_function

from flask_script import Command, Option

import os,sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app

from skylines.database import db
from skylines.model import User


from skylines.common import readfileNoStrip


class Email(Command):
    """ Send email to admins, a test site, or all users """

    option_list = (
        Option("path", help="path to a text file with the content of the email"),
        Option("to", help="can be 'admin' (goes to ) or 'all'")
    )

    def sendEmail(self, user, sender, recipient, subject, text, html):
        print("Sending email to {} (ID: {})...".format(user.name.encode("utf-8"),user.id))
        print(format(user.email_address))
        try:
            msg = MIMEMultipart('alternative')
            msg["Subject"] = subject
            msg["From"] = sender
            plain_part = 'Hi {},\n'.format(user.name.encode("utf-8").split(' ')[0])
            if text:
                plain_part += text
            plain = MIMEText(plain_part, 'plain')
            msg.attach(plain)
            if html:
                html = MIMEText(html, 'html') #any html should be last
                msg.attach(html)
            s = smtplib.SMTP('localhost')
            s.sendmail(sender, recipient.encode("ascii"), msg.as_string())
            s.quit()
        except BaseException as e:
            print(recipient)
            print("Sending email failed: {}".format(e))
            sys.exit('Stop')

    def run(self, path_plain, path_html, audience, test_address=None):
        '''test option it to send one email to a site like www.mail-tester.com'''
        if audience not in ['admin','all','test']:
            sys.exit('Stop: last option must be "admin", "all" or "test"')
        sender = 'mail@skylinscondor.com'
        os.chdir('/home/bret/servers/repo-skylinesC/skylinesC')
        lines_plain = readfileNoStrip(path_plain)
        lines_html = readfileNoStrip(path_html)
        subject = lines_plain[0].strip()
        text = ''
        for line in lines_plain[1:]:
            text += line
        html = ''
        for line in lines_html:
            html += line
        html += "<br><p>For help contact skylinescondor@gmail.com.  Don't reply to this message.</p>"
        html += '<br><p>--Bret at SkylinesCondor</p>'
        if audience == 'test':
            user = db.session.query(User).filter(User.id == 6)
            recipient = test_address
            self.sendEmail(user, sender, recipient, subject, text, html)
        else:
            users_query = (db.session.query(User).filter(User.email_address != None).order_by(User.id))
            for user in users_query:
                recipient = user.email_address
                if audience == 'admin' and user.admin:
                    self.sendEmail(user,sender,recipient,subject,text,html)
                    # break
                elif audience == 'all':
        self.sendEmail(user,sender,recipient,subject,text, html)
