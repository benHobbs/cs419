#!/usr/bin/python

import random
import datetime
import smtplib
import time


def Mail_Me(app):
	server, port, password = '', 587, ''
	sender = ''
	recipient = ''
	
	body, subject = "", ""
	if app['action'] == "Scheduled":
		print "TRUE"
		subject = 'Advising Signup with McGrath, D Kevin confirmed for ' + app["last_name"] + ", " + app["first_name"]
		body = "Advising Signup with McGrath, D Kevin confirmed\n"
	else:
		print "FALSE"
		subject = 'Advising Signup Cancellation'
		body = "Advising Signup with McGrath, D Kevin CANCELLED\n"
	body += "Name: REDACTED\n"
	body += "Email: REDACTED @oregonstate.edu\n"
	body += "Date: " + str(app['date'].strftime("%A, %B %d, %Y")) + "\n"
	body += "Time: " + str(app['date'].strftime("%I:%M%p")) + " - "
	end_time = app['date'] + datetime.timedelta(minutes = 30)
	body += str(end_time.strftime("%I:%M%p"))
	body += "\n\n\nPlease contact support@engr.oregonstate.edu if you experience problems"
	body = "" + body + ""

	headers = ["From: " + sender,
           "Subject: " + subject,
           "To: " + recipient,
           "MIME-Version: 1.0",
           "Content-Type: text/html"]
	headers = "\r\n".join(headers)
 
	session = smtplib.SMTP(server, port)
 
	session.ehlo()
	session.starttls()
	session.ehlo
	session.login(sender, password)
 
	session.sendmail(sender, recipient, headers + "\r\n\r\n" + body)
	session.quit()

def generate_dates(start_date, end_date):
    td = datetime.timedelta(hours=24)
    current_date = start_date
    lst = []
    while current_date <= end_date:
        lst.append(current_date)
        current_date += td
    return lst

lst = []

for i in range(1,20):
	name = random.choice(["Angie Richards","Rhonda Hogan","Dwight Boone","Della Fletcher","Benjamin Goodwin","Russell Caldwell","Deanna Flowers","Bradford Harrington","Tabitha Rogers","Brian Rivera","Debra Pierce","Cory Cole","Alison Guzman","Roberto Howell","Joanna Morris","Hector Keller","Marcos Blair","Dana Griffith","Alicia Quinn","Roy Rios","Roger Foster","Mercedes Allen","Emilio Powell","Carol Townsend","Dixie Mclaughlin","Elias Ramsey","Elvira Carter","Felicia Montgomery","Karen Green","Shannon Henry","Orlando Hansen","Nicholas Ortiz","Heidi Watkins","Janis Phelps","Belinda Patton","Alton Rice","Miguel Miller","Max Bridges","Opal Walker","Bryant Daniel","Pauline Waters","Ella Myers","Brandy Garrett","Timothy Pratt","Julie Pittman","Leon Colon","Eddie Smith","Lawrence Houston","Catherine Swanson","Eduardo Baker"])
	first_name, last_name = name.split()
	start_date, end_date = datetime.date(2014, 10, 1), datetime.date(2014, 12, 18)
	app_date = datetime.datetime.combine(random.choice(generate_dates(start_date, end_date)), datetime.time(random.choice(range(8,17)), random.choice([00,15,30,45])))
	action = random.choice(["Scheduled"])

	curr_app = {
		"first_name"	:	first_name,
		"last_name"		:	last_name,
		"action" 		: 	action,
		"date"			:	app_date,
	}

	lst.append(curr_app)

	Mail_Me(curr_app)

	time.sleep(1)


print lst