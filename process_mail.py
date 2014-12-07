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
CONST_NAME = ""
#your email for sending
CONST_SENDER = ''
#your outlook email
CONST_RECIPIENT = ''
#path to email.txt log file
CONST_PATH = '/'

def main():
	#set path for output
	path = os.getcwd()

	#replace with destination folder from ~
	path += CONST_PATH
	
	#Read from STDIN
	try:
		full_email = sys.stdin.read();
		parsed_msg = email.message_from_string(full_email.strip())
	except:
		full_email = "Error parsing email from stdin:  "
		full_email += str(datetime.now())
	
	#Parse raw email
	m_to = parsed_msg['To']
	m_from = parsed_msg['From']
	m_subject = parsed_msg['Subject']
	m_body = capture_body_from_email(full_email)
	m_attendee = parse_name_from_subject(str(m_subject).split())
	m_dt = parse_datetime_from_body(m_body)
	
	#do not take any action until "Advising Singup" in subject line"
	if m_subject.find("Advising Signup") > -1:
		if m_subject.find("Advising Signup Cancellation") > -1:
			m_action = "CANCELLED"
			
			#cancel in database
			db = mysqldb_upload.class_db()
			db.connect()
			db.cancel(m_dt.strftime("%Y%m%dT%H%M%SZ"))
			db.close()	
			
		else:
			m_firstname, m_lastname = parse_names(m_attendee)
			m_action = "CONFIRMED"
			curr_app = {
				#'id' : row[0],
				"first_name"	:	m_firstname,
				"last_name"		:	m_lastname,
				"from_line" 	:	m_from,
				"to_line" 		: 	m_to,
				"subject" 		: 	m_subject,
				"action" 		: 	m_action,
				#NOTE. DATETIME.NOW() RETURNING None
				"date_received" : 	datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ"),
				"app_start" 	: 	m_dt.strftime("%Y%m%dT%H%M%SZ"),
				"active" 		: 	"1"
			}
			
			#Upload to database
			db = mysqldb_upload.class_db()
			db.connect()
			db.put(curr_app)
			db.close()	
		
		#Format and send appointment email
		send_appointment(m_subject, m_body, m_attendee, m_dt, m_action)
		
		#Write email out to file for troubleshooting
		outfile = open(path, 'w')
		sys.stdout = outfile
		print full_email
		outfile.close()

def parse_names(attendee):
	attendee = " ".join(attendee.split(","))
	attendee = attendee.split()
	for i in range(len(attendee)):
		if i == 0:
			lastname = attendee[i]
		if i == 1:
			firstname = attendee[i]
	return firstname, lastname
		
	
def capture_body_from_email(full_email):
	full_email = " ".join(full_email.split("\n"))
	full_email = full_email.split()
	body = ""
	record = False
	for word in full_email:
		if record == True:
			body += word + " "
		if word == "Content-Type:":
			record = True
	return body
	
def parse_name_from_subject(subject_in):
	record = False
	name = ""
	for word in subject_in:
		if record:
			name += word + " "
		if word == "for":
			record = True
	return name

def parse_datetime_from_body(body_in):
	record_date = False
	record_date_cnt = 0
	record_time = False
	record_time_cnt = 0
	date_strp = ""
	time_strp = ""
	skip = 0
	body_in = body_in.split()
	for word in body_in:
		if record_date and record_date_cnt < 3:
			date_strp += word + " "
			record_date_cnt+=1
		if record_time and record_time_cnt < 1:
			time_strp += word + " "
			record_time_cnt+=1
		if skip == 1:
			record_date = True
		if word == "Date:":
			skip += 1
		if word == "Time:":
			record_time = True
	date_in = date_strp+time_strp
	date_in = re.sub(r"(st|nd|rd|th),", ",", date_in)
	dt = datetime.datetime.strptime(date_in, '%B %d, %Y %I:%M%p ')
	
	return dt
	
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

	mailServer = smtplib.SMTP('smtp.gmail.com', CONST_PORT)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(login, password)
	mailServer.sendmail(fro, attendees, msg.as_string())
	mailServer.close()

main()