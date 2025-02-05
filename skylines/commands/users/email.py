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
        Option("path_plain", help="path to a text file with the first part of the email"),
        Option("path_html", help="path to an html file with the last part of the email"),
        Option("audience", help="can be 'admin', 'all', or 'test'"),
        Option("test_address", help="one email address'")
    )

    def sendEmail(self, user, sender, recipient, subject, text, html):
        from datetime import datetime
        timeFormat = '%Y-%m-%d.%H.%M.%S.%f'
        queue_dir = '/media/sf_landscapes-zip/mail'
        log_file = os.path.join(queue_dir,'emails.log')
        if not os.path.exists(queue_dir):
            os.mkdir(queue_dir)
        print("Queueing email to {} (ID: {})...".format(user.name.encode("utf-8"),user.id))
        print(format(user.email_address))
        #try:
        if True:
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

            file_name = datetime.now().strftime(timeFormat) + '_skylinesC'
            f = open(os.path.join(queue_dir,file_name),'w')
            f.write(msg.as_string())
            f.close()
            f = open(log_file,'a')
            f.write(msg.as_string())
            f.close()
            # s = smtplib.SMTP('skylinescondor.com')
            # s.sendmail(sender, recipient.encode("ascii"), msg.as_string())
            # s.quit()
        #except BaseException as e:
         #   print(recipient)
          #  print("Queueing email failed: {}".format(e))
           # sys.exit('Stop')

    def run(self, path_plain, path_html, audience, test_address=None):
        '''test option is to send one email to a site like www.mail-tester.com'''
        if audience not in ['admin','all','test']:
            sys.exit('Stop: audience must be "admin", "all" or "test"')
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
        html += "<br><p>For help contact skylinescondor@gmail.com.  Don't reply to this message.</p>\n"
        html += '<br><p>--Bret at SkylinesCondor</p>\n'
        if audience == 'test':
            users = (db.session.query(User).filter(User.id == 6))
            recipient = test_address
            self.sendEmail(users[0], sender, recipient, subject, text, html)
        else:
            users_query = (db.session.query(User).filter(User.email_address != None).order_by(User.id))
            for user in users_query:
                recipient = user.email_address
                if audience == 'admin' and user.admin:
                    self.sendEmail(user,sender,recipient,subject,text,html)
                elif audience == 'all':
                    self.sendEmail(user, sender, recipient, subject, text)

