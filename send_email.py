# Script to email an attachment and list of people
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import os


def generate(sender, receiver, subject, body):
    # email formatting
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # #process and add attachment to email
    # filename = os.path.basename(path)
    # mime_type, _ = mimetypes.guess_type(path)
    # mime_type, mime_subtype = mime_type.split('/', 1)

    # with open(path, 'rb') as file:
    # 	msg.add_attachment(file.read(),
    # 		maintype = mime_type,
    # 		subtype = mime_subtype,
    # 		filename = filename)

    return msg


def send(msg):
    session = smtplib.SMTP("smtp.gmail.com", 587)
    session.starttls()
    session.login(sender, password)
    session.send_message(msg)
    session.quit()
    print("\nMail successfully sent.")


# <-------------------------------------------------->


# create message here
subject = "TEST SCRIPT"
body = "Hello, this is a test mail."

# sender and receiver details
sender = "sender@gmail.com"
password = "print(hello)"
receiver = "receiver@gmail.com"
#please change the receiver accordingly to receive the mails

if __name__ == "__main__":
    mail = generate(sender, receiver, subject, body)
    send(mail)

