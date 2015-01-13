#!/usr/bin/python

import sys
import smtplib


send_from = "email@whatever.com"
send_to = sys.argv[1]
textfile = sys.argv[2]

fp = open(textfile, "rb")

header = """To: "%s"\nFrom: "%s"\nSubject: %s\n\n""" % (send_to, send_from,
                                                        fp.readline())

msg = fp.read()
fp.close()
content = header + msg

s = smtplib.SMTP("smtp.gmail.com:587")
s.ehlo()
s.starttls()
s.login("username", "password")
s.sendmail(send_from, send_to, content)
s.quit()
