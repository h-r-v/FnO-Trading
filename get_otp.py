#modules
import imaplib
import email
from datetime import datetime

def get_otp():
    #date
    today = datetime.now().strftime("%d %b %Y")

    #credentials
    username ="manju2009enterprise@gmail.com"

    #generated app password
    app_password= "vcvfbapqtnvvedrj"

    # https://www.systoolsgroup.com/imap/
    gmail_host= 'imap.gmail.com'

    #set connection
    mail = imaplib.IMAP4_SSL(gmail_host)

    #login
    mail.login(username, app_password)

    #select inbox
    mail.select("INBOX")

    #target email
    target_email='accesscode@kotaksecurities.com'

    #select specific mails
    _, selected_mails = mail.search(None, f'(FROM "{target_email}")')

    #total number of mails from specific user
    #print(f"Total Messages from {target_email}:" , len(selected_mails[0].split()))

    otp = None

    for num in selected_mails[0].split():
        _, data = mail.fetch(num , '(RFC822)')
        _, bytes_data = data[0]

        email_message = email.message_from_bytes(bytes_data)

        if email_message['date'].split()[:3]==today.split():
            for part in email_message.walk():
                if part.get_content_type() == 'text/html':
                    body = email_message.as_bytes().decode(encoding='ISO-8859-1')
                    otp = body[body.find('XXXRN')+29:body.find('XXXRN')+33]
                    break
        
        if otp is not None:
            break

    mail.close()
    mail.logout()
    return otp

if __name__=='__main__':
    print(get_otp())

        