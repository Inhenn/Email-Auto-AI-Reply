import smtplib
import time
import imaplib
import email
import pandas as pd
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from chatterbot import ChatBot
import csv

ORG_EMAIL   = "@gmail.com"
FROM_EMAIL  = "mth4300group1" + ORG_EMAIL
FROM_PWD    = "pythonemail123"
SEND_SMTP_SERVER = 'smtp.gmail.com'
SEND_SMIP_PORT = 587
READ_SMTP_SERVER = "imap.gmail.com"
READ_SMTP_PORT   = 993
sendFrom = 'mth4300group1@gmail.com'

# ------------------------------------------------
def send_hello_email():
    with open('EmailAddressList.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            sendTo = row[0]     #row[0] represents the first element in each row which is email address!
            firstEmail = MIMEMultipart()
            firstEmail['Subject'] = 'Welcome to Group1 Ultra AI Chatting System!'
            body = 'Hello ' + row[1] + '. ' + 'Feel free to ask me any question.'
            firstEmail.attach(MIMEText(body, 'plain'))
            text = firstEmail.as_string()
            send_first_email = smtplib.SMTP(SEND_SMTP_SERVER, SEND_SMIP_PORT)
            send_first_email.ehlo()
            send_first_email.starttls()
            send_first_email.login(FROM_EMAIL, FROM_PWD)
            send_first_email.sendmail(sendFrom, sendTo, text)
            send_first_email.close()

# ------------------------------------------------

class myEmail():
    fromWhom = ''
    toWhom = ''
    subject = ''
    body = ''

# ------------------------------------------------

#YOU NEED TO PIP INSTALL THIS PACKAGE CALLED ChatBot/chatterbot


def read_email_from_gmail():

    chatbot = ChatBot('Ron Obvious', trainer='chatterbot.trainers.ChatterBotCorpusTrainer')

    # Train based on the english corpus
    chatbot.train("chatterbot.corpus.english")
    #
    # # # Train based on english greetings corpus
    chatbot.train("chatterbot.corpus.english.greetings")
    # #
    # # # Train based on the english conversations corpus
    chatbot.train("chatterbot.corpus.english.conversations")

    try:
        readEmail = imaplib.IMAP4_SSL(READ_SMTP_SERVER)
        readEmail.login(FROM_EMAIL,FROM_PWD)
        readEmail.select('inbox')

        type, data = readEmail.search(None, 'ALL')
        print data

        mail_ids = data[0]

        id_list = mail_ids.split()
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

        sendEmail = smtplib.SMTP(SEND_SMTP_SERVER, SEND_SMIP_PORT)
        sendEmail.ehlo()
        sendEmail.starttls()
        sendEmail.login(FROM_EMAIL,FROM_PWD)##Basic login to the email server

        while(True):
            try:
                for i in range(first_email_id,latest_email_id+1,1):

                    typ, data = readEmail.fetch(i, '(RFC822)')
                    receivedEmail = myEmail()
                    readEmail.store(i, '+FLAGS', '\\Deleted')

                    for response_part in data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_string(response_part[1])
                            receivedEmail.fromWhom = msg['from']
                            receivedEmail.subject = msg['subject']
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":  # ignore attachments/html
                                    body = part.get_payload(decode=True)
                                    receivedEmail.body = body
                            replyEmail = MIMEMultipart()
                            replyEmail['Subject'] = 'Reply'
                            onelineMsg = str(receivedEmail.body)
                            try:
                                onelineMsg = onelineMsg.split("\n")[0]
                            except:
                                pass
                            msgbody = str(chatbot.get_response(onelineMsg))

                            print 'Look at this email'
                            print 'From : ' + receivedEmail.fromWhom
                            print 'Subject : ' + receivedEmail.subject
                            print 'Body : ' + onelineMsg

                            replyEmail.attach(MIMEText(msgbody, 'plain'))
                            text = replyEmail.as_string()
                            sendEmail.sendmail(sendFrom, receivedEmail.fromWhom, text)

                readEmail.expunge()

            except:
                pass
            time.sleep(5)

                    # print 'From : ' + email_from + '\n'
                    # print 'Subject : ' + email_subject + '\n'

    except Exception, e:
        print str(e)

if __name__ == '__main__':
    send_hello_email()
    read_email_from_gmail()
