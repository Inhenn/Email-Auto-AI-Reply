import smtplib
import time
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from chatterbot import ChatBot
#YOU NEED TO PIP INSTALL THIS PACKAGE CALLED ChatBot/chatterbot

ORG_EMAIL   = "@gmail.com" #gmail account by default
FROM_EMAIL  = "YOUR GMAIL ACCOUNT NAME(without @gmail.com)" + ORG_EMAIL
FROM_PWD    = "YOUR GMAIL ACCOUNT PASSWORD"
SEND_SMTP_SERVER = 'smtp.gmail.com'#gmail account by default
SEND_SMIP_PORT = 587
READ_SMTP_SERVER = "imap.gmail.com"#gmail account by default
READ_SMTP_PORT   = 993




class myEmail():
    fromWhom = ''
    toWhom = ''
    subject = ''
    body = ''

# ------------------------------------------------




def read_email_from_gmail():

#************the following code is training the chatterbot********************************
    chatbot = ChatBot('Ron Obvious', trainer='chatterbot.trainers.ChatterBotCorpusTrainer')

    # Train based on the english corpus
    chatbot.train("chatterbot.corpus.english")
    #
    # # # Train based on english greetings corpus
    chatbot.train("chatterbot.corpus.english.greetings")
    # #
    # # # Train based on the english conversations corpus
    chatbot.train("chatterbot.corpus.english.conversations")
#********************************************************************************************
    try:
        readEmail = imaplib.IMAP4_SSL(READ_SMTP_SERVER)
        readEmail.login(FROM_EMAIL,FROM_PWD)
        readEmail.select('inbox')

        type, data = readEmail.search(None, 'ALL')
        print data

        mail_ids = data[0]

        id_list = mail_ids.split()
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])#get the whole email list

        sendEmail = smtplib.SMTP(SEND_SMTP_SERVER, SEND_SMIP_PORT)
        sendEmail.ehlo()
        sendEmail.starttls()
        sendEmail.login(FROM_EMAIL,FROM_PWD)

        while(True):
            try:
                for i in range(first_email_id,latest_email_id+1,1):

                    typ, data = readEmail.fetch(i, '(RFC822)')
                    receivedEmail = myEmail()
                    readEmail.store(i, '+FLAGS', '\\Deleted')# mark the read email and delete it in the end

#*****************The following code is to read the content of the email************************************************

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


                            print 'Look at this email'
                            print 'From : ' + receivedEmail.fromWhom
                            print 'Subject : ' + receivedEmail.subject
                            print 'Body : ' + onelineMsg

#****************************************The following code is to reply *************************************************************

                            msgbody = str(chatbot.get_response(onelineMsg))
                            replyEmail.attach(MIMEText(msgbody, 'plain'))
                            text = replyEmail.as_string()
                            sendEmail.sendmail(FROM_EMAIL, receivedEmail.fromWhom, text)

                readEmail.expunge()#delete the read email

            except:
                pass
            time.sleep(5)



    except Exception, e:
        print str(e)

if __name__ == '__main__':

    read_email_from_gmail()
