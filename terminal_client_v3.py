#!/usr/bin/python

import curses
import mysqldb_upload
import datetime
import time
import send_app

from curses import wrapper

class terminal_client:
	def __init__(self, client_info):
		#setup colors for the client screen
		curses.use_default_colors()

		#curses.init_pair(1, -1, -1)
		curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)

		#turn cursor off
		curses.curs_set(0)
		
		#set vars
		self.width = 150
		self.header_height = 1
		self.footer_height = 1
		self.inbox_width = 88
		self.msg = "Hello, Running..."
		self.search_term = "No Current Search"

		# Derived Settings
		self.screen = client_info['screen']
		self.start_x = client_info['start_x'] 
		self.start_y = client_info['start_y']
		self.height = client_info['client_height']
		self.body_height = self.height - 2
		self.inbox_height = self.height - 4
		self.content_height = self.height - 4
		self.content_width = self.width - self.inbox_width

		# Line Vars
		self.lines = []
		self.current_line = 0
		self.start_index = 0
		
		# Setup default sort
		self.default_sort = 'date_received'
		self.sort_reverse = False
		
		# Get data
		self.empty_set = True
		self.number_records = 0
		self.last_update = datetime.time(0, 0)
		self.lst = []
		self.get_list()

		# Search Stuff
		self.lst_search = []
		self.search_active = False

		# Sort data
		self.sort_list(self.default_sort)


	def draw(self):
		#build header window
		self.header = curses.newwin(self.header_height,self.width,self.start_y,self.start_x)
		self.header.bkgd(' ', curses.color_pair(2))

		#build inbox window
		self.inbox = curses.newwin(self.body_height,self.inbox_width,self.start_y + self.header_height,self.start_x)
		self.inbox.bkgd(' ', curses.color_pair(1))
		self.inbox.border()

		#build content window
		self.content = curses.newwin(self.body_height,self.content_width,self.start_y + self.header_height,self.inbox_width + 1)
		self.content.bkgd(' ', curses.color_pair(1))
		self.content.border()

		#build footer window
		self.footer = curses.newwin(self.header_height,self.width,self.start_y + self.header_height + self.body_height,self.start_x)
		self.footer.bkgd(' ', curses.color_pair(2))

		#refresh screens
		self.screen.refresh();self.header.refresh();self.inbox.refresh(); self.content.refresh(); self.footer.refresh()

		#load windows
		self.load_header(); self.load_inbox(); self.load_inbox_content(); self.setup_content(); self.load_footer()

	def load_header(self):
		header_text = 'q: quit | u: update | s: search | ?: help'
		self.header.addstr(0,1,header_text)
		self.header.addstr(0,1,'q',curses.A_UNDERLINE)
		self.header.addstr(0,11,'u',curses.A_UNDERLINE)
		self.header.addstr(0,23,'s',curses.A_UNDERLINE)
		self.header.addstr(0,35,'?',curses.A_UNDERLINE)
		self.header.refresh()

	def load_inbox(self):
		#set current line to 0 (first line highlighted)
		self.current_line = 0
		self.line_width = self.inbox_width - 2
		self.num_lines = self.body_height - 6
		self.inbox.addstr(1,2,'#')
		self.inbox.addstr(1,8,'date received')
		self.inbox.addstr(1,8,'d',curses.A_UNDERLINE)
		self.inbox.addstr(1,26,'student name')
		self.inbox.addstr(1,27,'t',curses.A_UNDERLINE)
		self.inbox.addstr(1,58,'action')
		self.inbox.addstr(1,58,'a',curses.A_UNDERLINE)
		self.inbox.addstr(1,69,'appointment time')
		self.inbox.addstr(1,83,'m',curses.A_UNDERLINE)
		self.inbox.addstr(2,1,"-" * (self.inbox_width - 2))
		self.inbox.addstr(self.body_height-3,1,"-" * (self.inbox_width - 2))
		self.inbox.refresh()

	def load_footer(self):
		self.footer.addstr(0,self.width - self.content_width + 1, ' ' * (self.content_width - 2 )) # clear line
		self.footer.addstr(0,self.width - self.content_width + 1, 'Message: %s' % self.msg)
		self.footer.addstr(0,8, ' ' * 25)
		self.footer.addstr(0,1,'Search: %s' % self.search_term)
		self.footer.refresh()

	def load_inbox_content(self, cur_line=0, start_index=0):
		if not self.search_active:
			lst = self.lst
		else:
			lst = self.lst_search

		self.current_line = cur_line
		self.start_index = start_index
		#make a list of windows where lines[0] is the first line
		for i in range (0, self.num_lines):
			self.lines.append(curses.newwin(1,self.line_width,self.start_y + 4 + i,self.start_x + 1))
			if i == cur_line:
				self.lines[i].bkgd(' ', curses.color_pair(2))
			else:
				self.lines[i].bkgd(' ', curses.color_pair(1))
			self.lines[i].erase()
			self.lines[i].refresh()

		line = 0
		for record in lst[start_index:start_index+self.num_lines]:
			self.lines[line].addstr(0,1,'%s.' % str(int(line + start_index) + 1))
			self.lines[line].addstr(0,7,datetime.datetime.strptime(record['date_received'], "%Y%m%dT%H%M%SZ").strftime('%m-%d-%Y %H:%M'))
			self.lines[line].addstr(0,25,'%s, %s' % (record['last_name'], record['first_name']))
			self.lines[line].addstr(0,57,record['action'])
			self.lines[line].addstr(0,68,datetime.datetime.strptime(record['app_start'], "%Y%m%dT%H%M%SZ").strftime('%m-%d-%Y %H:%M'))
			self.lines[line].refresh()
			line += 1

		# Format Inbox Footer
		self.inbox.addstr(self.body_height-2,2,'Total Records: %s' % "    ")
		self.inbox.addstr(self.body_height-2,2,'Total Records: %s' % str(self.number_records))
		self.inbox.addstr(self.body_height-2,self.inbox_width-40,' ' * 39)
		self.inbox.addstr(self.body_height-2,self.inbox_width-40,'Last Update: %s' % str(self.last_update))
		self.inbox.refresh()

	def setup_content(self):
		self.content.addstr(1,2,'cancel appointment')
		self.content.addstr(1,2,'c',curses.A_UNDERLINE)
		self.content.addstr(2,1,"-" * (self.content_width - 2))
		self.content.addstr(self.body_height-3,1,"-" * (self.content_width - 2))

		content_window = curses.newwin(self.content_height - 4, self.content_width - 2, self.start_y + 4, self.start_x + self.inbox_width + 1)
		content_window.bkgd(' ', curses.color_pair(1))
		content_window.erase()
		content_window.refresh()

		if not self.empty_set:
			self.content.addstr(3,2,'To:\t\t%s' % str(self.lst[(self.current_line + self.start_index)]['to']))
			self.content.addstr(4,2,'From:\t\t%s' % str(self.lst[(self.current_line + self.start_index)]['from']))
			self.content.addstr(5,2,'Date:\t\t%s' % datetime.datetime.strptime(self.lst[(self.current_line + self.start_index)]['date_received'], "%Y%m%dT%H%M%SZ").strftime('%m-%d-%Y %H:%M'))
			self.content.addstr(6,2,'Subject:\t%s' % str(self.lst[(self.current_line + self.start_index)]['subject'])[:37])
			self.content.addstr(7,2,'\t\t%s' % str(self.lst[(self.current_line + self.start_index)]['subject'])[38:])
			self.content.addstr(9,2,'Appointment:\t%s - %s' % (datetime.datetime.strptime(self.lst[(self.current_line + self.start_index)]['app_start'], "%Y%m%dT%H%M%SZ").strftime('%m-%d-%Y %H:%M'),
																	datetime.datetime.strptime(self.lst[(self.current_line + self.start_index)]['app_end'], "%Y%m%dT%H%M%SZ").strftime('%m-%d-%Y %H:%M')))

		self.content.refresh()


	def move(self, up):	#up is a bool, true means move up
		prev_line = self.current_line
		if up:
			if self.current_line > 0:									# not on top line
				self.current_line -= 1
				self.lines[prev_line].bkgd(' ', curses.color_pair(1))
				self.lines[self.current_line].bkgd(' ', curses.color_pair(2))
				self.lines[prev_line].refresh(); self.lines[self.current_line].refresh();
			elif self.current_line == 0 and self.start_index > 0:		# on top line, but not at top of list
				self.load_inbox_content(0, self.start_index-1)
			else:
				exit
		else:
			if self.current_line < self.num_lines - 1 and self.current_line + self.start_index + 1 < self.number_records:
				self.current_line += 1
				self.lines[prev_line].bkgd(' ', curses.color_pair(1))
				self.lines[self.current_line].bkgd(' ', curses.color_pair(2))
				self.lines[prev_line].refresh(); self.lines[self.current_line].refresh();
			elif self.current_line == self.num_lines - 1 and self.current_line + self.start_index + 1 < self.number_records:
				self.load_inbox_content(self.current_line, self.start_index + 1)
			else:
				exit

		self.setup_content()

	def search(self):
		#build search window over the top of the client
		search_win = curses.newwin(3,self.inbox_width - 6,self.start_y + 11 ,self.start_x + 3)
		search_win.bkgd(' ', curses.color_pair(1))
		search_win.addstr(1,1,'search: ')
		search_win.border()
		search_win.refresh()

		#enable cursor and echo
		curses.curs_set(1); curses.echo()

		#get search term
		self.search_term = search_win.getstr(1,9,25).lower()
		
		#disable cursor and echo
		curses.noecho(); curses.curs_set(0)

		self.lst_search = []
		if not self.search_term == "":
			self.search_active = True
			for index, record in enumerate(self.lst):
				if self.search_term in record['last_name'].lower() or self.search_term in record['first_name'].lower():
					self.lst_search.append(record)
			self.number_records = len(self.lst_search)
		else:
			self.search_active = False
			self.search_term = "No Current Search"
			self.number_records = len(self.lst)
		
		self.load_inbox_content()
		self.load_footer()

	def cancel_app(self):
		# Build cancel insure window over client
		cancel_win = curses.newwin(3, self.content_width - 4, self.start_y + 11, self.start_x + self.inbox_width + 2)
		cancel_win.addstr(1,1,'Really Cancel(y/n): ')
		cancel_win.border()
		cancel_win.refresh()

		curses.curs_set(1); curses.echo()			#enable cursor and echo
		cancel_value = cancel_win.getstr(1,21,1)	# Get Insure Value
		curses.noecho(); curses.curs_set(0)			#disable cursor and echo

		if cancel_value == 'y':
			db = mysqldb_upload.class_db()
			db.connect()

			record = self.lst[self.current_line + self.start_index]
			m_dt = datetime.datetime.strptime(record['app_start'], "%Y%m%dT%H%M%SZ")

			db.cancel(m_dt.strftime("%Y%m%dT%H%M%SZ"))
			db.close()
			self.msg = "Cancellation Successful"
			self.lst.pop((self.current_line + self.start_index))
			if len(self.lst) != 0:
				self.empty_set = False					# Is Not Empty Set
				self.number_records = len(self.lst)		# Set number of records to correct number of records
			else:
				self.empty_set = True 					# Is Empty Set
				self.number_records = 0					# Set number of records to 0

			send_app.send_appointment("Appointment Canceled",
										"Appointment with " + record['last_name'] + ", " + record['first_name'] + " has been canceled.  In other news, it is 5 o'clock somewhere.",
										"attendee",
										datetime.datetime.strptime(self.lst[(self.current_line + self.start_index)]['app_start'], '%Y%m%dT%H%M%SZ'),
										"CANCELLED")
		elif cancel_value == 'n':
			self.msg = "Cancellation Canceled, Oh The Irony"
		else:
			self.msg = "Unrecognized Value"

		self.load_inbox_content()
		self.setup_content()
		self.load_footer()

	def get_list(self):
		# Get data
		db = mysqldb_upload.class_db()
		db.connect()
		self.lst = db.get()
		db.close()

		if len(self.lst) != 0:
			self.empty_set = False					# Is Not Empty Set
			self.number_records = len(self.lst)		# Set number of records to correct number of records
		else:
			self.empty_set = True 					# Is Empty Set
			self.number_records = 0					# Set number of records to 0

		# Set last_update field to current time
		self.last_update = time.strftime("%c")

	def sort_list(self, sort):
		if sort == "":
			self.default_sort = 'date_received'
			self.sort_reverse = False
			self.lst = sorted(self.lst, key=lambda k: k[self.default_sort])
		elif sort == self.default_sort:
			if self.sort_reverse:
				self.lst = sorted(self.lst, key=lambda k: k[sort])
				self.sort_reverse = False
			else:
				self.lst = sorted(self.lst, key=lambda k: k[sort], reverse=True)
				self.sort_reverse = True
		else:
			self.default_sort = sort
			self.sort_reverse = False
			self.lst = sorted(self.lst, key=lambda k: k[sort])

	def update(self):
		self.get_list()
		self.sort_list('')
		self.load_inbox_content()
		self.setup_content()

	def close(self):
		curses.curs_set(1)

	def start(self):
		while True:
			ch = self.screen.getch()
			if ch == ord('q'): self.close(); break				#quit
			elif ch == 63: self.get_info()						#help
			elif ch == 99:
				self.cancel_app()								#cancel						
			elif ch == 115:	self.search()						#search
			elif ch == 117: self.update()						#update
			elif ch == 258: self.move(False)					#down
			elif ch == 259:	self.move(True)						#up
			elif ch == 336: self.move_scrolling(False)			#down
			elif ch == 337: self.move_scrolling(True)			#up
			elif ch == 100:			#sort date_received
				self.sort_list('date_received')
				self.load_inbox_content() 	
				self.setup_content()
			elif ch == 116:			#sort last_name
				self.sort_list('last_name')
				self.load_inbox_content() 		
				self.setup_content()
			elif ch == 97:			#sort action type
				self.sort_list('action')
				self.load_inbox_content()
				self.setup_content()
			elif ch == 109:			#sort app_time
				self.sort_list('app_start')
				self.load_inbox_content()
				self.setup_content()
			else:
				self.screen.addstr(0,0,"     ")
				self.screen.addstr(0,0,str(ch))
				self.screen.refresh()

def main(screen):
	#setup client options (sizes)
	client_info = {	'screen' : screen,
					'start_x': 1,
					'start_y': 1,
					'client_height': 30}

	#initialize client
	client = terminal_client(client_info)			#init client as terminal_client object
	client.draw()									#draw terminal
	client.start()
		
wrapper(main)
