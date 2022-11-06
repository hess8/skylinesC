from __future__ import absolute_import, print_function

from flask_script import Command, Option

import io
import sys, smtplib, ssl
from email.mime.text import MIMEText
from email.utils import formatdate
from flask import current_app

from skylines.database import db
from skylines.model import User


class Email(Command):
    """ Send email to all users """



    option_list = (
        Option("path", help="path to a text file with the content of the email"),
    )

    def run(self, path):
        sender = 'skylinescondor@soardata.org'
        with io.open(path, mode="r", encoding="utf-8") as f:
            content = f.read()
            title, text = [str.strip() for str in content.split("---")]

        users_query = (
            db.session.query(User).filter(User.email_address != None).order_by(User.id)
        )

        for user in users_query:
            print(
                u"Sending email to {} (ID: {})...".format(user.name, user.id).encode(
                    "utf-8"
                )
            )

            try:
                custom_text = u"Hello {},\n\n{}".format(user.name, text)

                smtp = smtplib.SMTP('localhost')
                msg = MIMEText(custom_text.encode("utf-8"), "plain", "utf-8")
                msg["Subject"] = title.encode("utf-8")
                msg["From"] = sender
                msg["To"] = user.email_address.encode("ascii")
                # smtp.ehlo()
                smtp.sendmail(
                    current_app.config["EMAIL_FROM"].encode("ascii"),
                    user.email_address.encode("ascii"),
                    msg.as_string(),
                )
                smtp.quit()

            except BaseException as e:
                print("Sending email failed: {}", e)
