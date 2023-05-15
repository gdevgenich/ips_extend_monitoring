from socket import gethostname
from smtplib import SMTP
from email.message import EmailMessage

TO = "dgirdyuk@intermedia.com"
SUBJECT = "Python test email"
BODY = "test message"

def send_report(to, subject, body, relay="localhost"):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = gethostname() + '@intermedia.net'
    msg['To'] = to
    s = SMTP(relay)
    s.send_message(msg)
    s.quit()


if __name__ == "__main__":
    send_report(TO, SUBJECT, BODY)