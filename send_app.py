#!/usr/bin/python

import sys
import email
import os
import smtplib
#from datetime import datetime
import time
import mysqldb_upload
import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import re

#your sending email server
CONST_SERVER = ''
#your sending email port
CONST_PORT = 587
#your sending email password
CONST_PW = ''
#your sending email name
CONST_NAME = ''
#your email for sending
CONST_SENDER = ''
#your outlook email
CONST_RECIPIENT = ''

def send_appointment(subj, description, visitor, when, action):
#Baseline ICS Formatting from: http://stackoverflow.com/questions/4823574/sending-meeting-invitations-with-python
	CRLF = "\r\n"
	login = CONST_SENDER
	password = CONST_PW
	attendees = [CONST_RECIPIENT]
	organizer = "ORGANIZER;CN="+CONST_SENDER+":mailto:"+CONST_SENDER
	fro = CONST_NAME + " <"+CONST_RECIPIENT+">"
	dur = datetime.timedelta(minutes = 15)
	ddtstart = when
	dtend = ddtstart + dur
	dtstamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
	dtstart = ddtstart.strftime("%Y%m%dT%H%M%SZ")
	dtend = dtend.strftime("%Y%m%dT%H%M%SZ")
	
	if action == "CANCELLED":
		method = "CANCEL"
		sequence = str(1)
	else:
		method = "REQUEST"
		sequence = str(0)

	attendee = ""
	for att in attendees:
		attendee += "ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-    PARTICIPANT;PARTSTAT=ACCEPTED;RSVP=TRUE"+CRLF+" ;CN=organizer;X-NUM-GUESTS=0:"+CRLF+" mailto:"+att+CRLF
	ical = "BEGIN:VCALENDAR"+CRLF+"PRODID:pyICSParser"+CRLF+"VERSION:2.0"+CRLF+"CALSCALE:GREGORIAN"+CRLF
	ical+="METHOD:"+method+CRLF+"BEGIN:VEVENT"+CRLF+"DTSTART:"+dtstart+CRLF+"DTEND:"+dtend+CRLF+"DTSTAMP:"+dtstart+CRLF+organizer+CRLF
	ical+= "UID:STDNTAPPT"+dtstamp+CRLF
	ical+= attendee+"CREATED:"+dtstamp+CRLF+subj+CRLF+"LAST-MODIFIED:"+dtstamp+CRLF+"LOCATION:"+CRLF+"SEQUENCE:"+sequence+CRLF+"STATUS:"+action+CRLF
	ical+= "SUMMARY:"+subj+CRLF+"TRANSP:OPAQUE"+CRLF+"END:VEVENT"+CRLF+"END:VCALENDAR"+CRLF

	eml_body = description
	eml_body_bin = description
	msg = MIMEMultipart('mixed')
	msg['Reply-To']=fro
	msg['Date'] = formatdate(localtime=True)
	msg['Subject'] = subj+dtstart
	msg['From'] = fro
	msg['To'] = ",".join(attendees)

	part_email = MIMEText(eml_body,"html")
	part_cal = MIMEText(ical,'calendar;method=REQUEST')

	msgAlternative = MIMEMultipart('alternative')
	msg.attach(msgAlternative)

	ical_atch = MIMEBase('application/ics',' ;name="%s"'%("invite.ics"))
	ical_atch.set_payload(ical)
	Encoders.encode_base64(ical_atch)
	ical_atch.add_header('Content-Disposition', 'attachment; filename="%s"'%("invite.ics"))

	eml_atch = MIMEBase('text/plain','')
	Encoders.encode_base64(eml_atch)
	eml_atch.add_header('Content-Transfer-Encoding', "")

	msgAlternative.attach(part_email)
	msgAlternative.attach(part_cal)

	mailServer = smtplib.SMTP(CONST_SERVER, CONST_PORT)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(login, password)
	mailServer.sendmail(fro, attendees, msg.as_string())
	mailServer.close()