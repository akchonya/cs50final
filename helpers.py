import os
import re
import smtplib

from flask import render_template, session, request, url_for, redirect
from functools import wraps
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from cs50 import SQL

db = SQL("sqlite:///data/data.db")

# Decorate routes to require email verification
def email_validation(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = db.execute("SELECT email_validation FROM users WHERE id = ?", session["user_id"])
        if len(token) != 1:
            return redirect("/confirm_email")
        if not token[0]["email_validation"]:
            return redirect("/confirm_email")
        return f(*args, **kwargs)
    return decorated_function


# Decorate routes to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Validate an email
def valid_email(email):
    # Regular expression
    regex = "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"
    if re.fullmatch(regex, email):
        return True
    return False 


# Validate an username
def valid_username(username):
    regex = "^[A-Za-z0-9_]+$"
    if re.match(regex, username):
        return True
    return False 


# Sending a confirmation link to an given email 
def send_email(token, email, msg):
    # Config values
    smtpHost = "smtp.gmail.com"
    smtpPort = 587
    mailUname = "narutotraker@gmail.com"
    mailPwd = "xtuotadnnpeebvcr"
    fromEmail = "narutotraker@gmail.com"
    

    mailSubject = "Confirm Email"
    mailContentHtml = msg
    recepientsMailList = [email]

    msg = MIMEMultipart()
    msg["From"] = fromEmail
    msg["To"] = email
    msg["Subject"] = mailSubject
    msg.attach(MIMEText(mailContentHtml, 'html'))

    # Send message object as email using smptplib
    server = smtplib.SMTP(smtpHost, smtpPort)
    server.starttls()
    server.login(mailUname, mailPwd)
    msgText = msg.as_string()
    sendErrs = server.sendmail(fromEmail, recepientsMailList, msgText)
    server.quit()

    # check if errors occured and handle them accordingly
    if not len(sendErrs.keys()) == 0:
        raise Exception("Errors occurred while sending email", sendErrs)

