# Python code to illustrate Sending mail with attachments
# from your Gmail account

# libraries to be imported
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from helper import log_dir
import datetime

def mail(instrument, error_flag, fromaddr = "princessbananahammock1999@gmail.com", toaddr = ["toharshrocks1@gmail.com","manjushreefinserve@gmail.com"], password="myraa1sep2020"):
    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = ','.join(toaddr)

    # storing the subject
    error_flag = 'Error Report' if error_flag else 'FnO Report' 
    msg['Subject'] = f'{instrument} {error_flag} ' + datetime.datetime.now().strftime("%m-%d-%Y")

    # string to store the body of the mail
    body = "Today's report"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = "main.txt"
    attachment = open(os.path.join(log_dir(instrument),'main.txt'), "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # open the file to be sent
    filename = "trade.txt"
    attachment = open(os.path.join(log_dir(instrument),'trade.txt'), "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, password)

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    if isinstance(toaddr,str):
        s.sendmail(fromaddr, toaddr, text)
    else:
        for i in toaddr:
            s.sendmail(fromaddr, i, text)

    # terminating the session
    s.quit()

if __name__=='__main__':
    mail()
