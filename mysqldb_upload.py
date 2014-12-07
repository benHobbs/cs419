#!/usr/bin/python	

import MySQLdb

class class_db:
	def __init__(self):
		self.host=''
		self.user=''
		self.password=''
		self.database=''

	# Connect to school database, must be run from a server with access
	def connect(self):
		self.db = MySQLdb.connect(self.host,self.user,self.password,self.database)
		self.cursor = self.db.cursor()

	# Puts curr_app (dictionary) into the db
	def put(self, curr_app):
		columns, values = "", ""
		for key, value in curr_app.iteritems():
			columns += key + ","
			values += value +"','"
		insert_statement = "INSERT INTO tbl_apps (" + columns[:-1] + ") VALUES ('" + values[:-3] + "')"
		self.cursor.execute(insert_statement)
		self.db.commit()

	# Returns list of total db
	def get(self):
		self.cursor = self.db.cursor()
		self.cursor.execute("SELECT * FROM tbl_apps WHERE active = '1'")
		lst = []
		for row in self.cursor.fetchall():
			curr_app = {
				'id' 			: row[0],
				'first_name' 	: row[1],
				'last_name' 	: row[2],
				'from' 			: row[3],
				'to' 			: row[4],
				'subject' 		: row[5],
				'action' 		: row[6],
				'date_received' : row[7],
				'app_start' 	: row[8],
				'app_end'		: row[9],
				'active' 		: row[10]
				}
			lst.append(curr_app)
		return lst
		
	# Returns appointment given time
	def find_when(self, time):
		self.cursor = self.db.cursor()
		self.cursor.execute("SELECT * FROM tbl_apps WHERE tbl_apps.app_start = "+time)
		lst = []
		for row in self.cursor.fetchall():
			curr_app = {
				'id' : row[0],
				'first_name' : row[1],
				'last_name' : row[2],
				'from' : row[3],
				'to' : row[4],
				'subject' : row[5],
				'action' : row[6],
				'date_received' : row[7],
				'app_start' : row[8],
				'app_end' : row[8],
				'active' : row[10]
				}
			lst.append(curr_app)
		return lst
	
	#cancels appointment at given time
	def cancel(self, time):
		self.cursor = self.db.cursor()
		self.cursor.execute("UPDATE tbl_apps SET action = 'CANCELLED', active = 0 WHERE app_start = '"+time+"' AND active = '1'")
		self.db.commit()
		
	# Close connections
	def close(self):
		self.cursor.close()
		self.db.close()
		
def test():
	print "Begin test of database"
	print "Put appointment into database"

	db = class_db()
	db.connect()
	db.put(curr_app)
	db.close()

	print "put successful"
	print "get all appointments in database"

	db_1 = class_db()
	db_1.connect()
	lst = db_1.get()
	db_1.close()

	print lst
	print "good to go"