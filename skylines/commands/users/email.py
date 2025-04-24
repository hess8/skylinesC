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
    """ Queue email to admins, a test site, or all users
        creates a text file for each email that email server
        on another machine will read
    """

    option_list = (
        Option("path_text", help="path file with the body in html except for p tags"),
        Option("audience", help="can be 'admin', 'all', or 'test'"),
        Option("test_address", help="one email address'")
    )

    def toHTML(self,line,user):
        if user.email_address == 'lubosf@centrum.cz':
            xx=0
        if line.strip()[:3] not in ['<p>','<br', '<hr']:
            newline =  '<p>{}</p>\n'.format(line.rstrip('\n'))
        else:
            newline =  line
        return newline.replace('$first_name', user.first_name).encode("utf-8")

    def queueEmail(self, user, sender, recipient, subject, text):
        from datetime import datetime
        timeFormat = '%Y-%m-%d.%H.%M.%S.%f'
        queue_dir = '/media/sf_shared_VMs/mail/queued'
        log_file = os.path.join(queue_dir,'emails.log')
        if not os.path.exists(queue_dir):
            os.mkdir(queue_dir)
        html = []
        for line in text:
            html.append(self.toHTML(line,user))
        html.append("<br><hr><p>For help contact skylinescondor@gmail.com.  Don't reply to this message.</p>\n")
        html.append('<br><p>--Bret at SkylinesCondor</p>\n')
        try:
            file_name = datetime.now().strftime(timeFormat) + '_skylinesC.msg'
            timeTag = datetime.now().strftime("%y/%m/%d %H:%M:%S")
            f = open(os.path.join(queue_dir,file_name),'w')
            f.write(sender + '\n')
            f.write(recipient + '\n')
            f.write(subject + '\n')
            f.writelines(html)
            f.close()
            f = open(log_file,'a')
            f.write('{} queu {} {} {}'.format(timeTag, recipient, sender, subject))
            f.close()
            print("Queued email to {} (ID: {}) {}".format(user.name.encode("utf-8"),user.id,user.email_address))
        except BaseException as e:
            print(recipient)
            print("Queueing email failed: {}".format(e), recipient, subject)
            sys.exit('Stop')

    def run(self, path_text, audience, test_address=None):
        '''test option is to send one email to a site like www.mail-tester.com'''
        if audience not in ['admin','all','test']:
            sys.exit('Stop: audience must be "admin", "all" or "test"')
        sender = 'mail@skylinescondor.com' #overwritten in mail-server
        os.chdir('/home/bret/skylinesC')
        lines = readfileNoStrip(path_text)
        #lines[0] is instructions to write html but leave out any paragraph markings
        subject = lines[1]
        text = lines[2:]
        if audience == 'test':
            users = (db.session.query(User).filter(User.id == 6))
            recipient = test_address
            self.queueEmail(users[0], sender, recipient, subject, text)
        else:
            users_query = (db.session.query(User).filter(User.email_address != None).order_by(User.id))
            for user in users_query:
                recipient = user.email_address
                if audience == 'admin' and user.admin:
                    self.queueEmail(user,sender,recipient,subject, text)
                elif audience == 'all':
                    self.queueEmail(user, sender, recipient, subject, text)

