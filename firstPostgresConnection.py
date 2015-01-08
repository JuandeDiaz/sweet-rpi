# 08 ene 2015
# aim: to insert data into a postgres database

# imports
import psycopg2

#  function to search the database 
def showDatabase():
	
	# first we try to connect
	try:
		conn=psycopg2.connect("dbname='slope_db' user='postgres' host='localhost' password='p@ssw0rd'")
		print('database connected!!'.encode('utf-8').decode('utf-8')) 
	except:
		print('I am unable to connect to the database'.encode('utf-8').decode('utf-8')) 
		conn.close()
	
	#then we create a cursor to connect
	cur=conn.cursor()
	
	#now we execute a query
	cur.execute("""SELECT * FROM tag_data""")
	
	#now we receive the result and then we print it
	result=cur.fetchall()	
	print("\nHere are the query results:\n".encode('utf-8').decode('utf-8'))
	for row in result:
		print ("   "+str(row[0])+"   "+str(row[1])+"   "+str(row[2]))
	
	#here we close the db connection
	cur.close()
	conn.close()

#  function to insert data
def insertData():
	
	# first we try to connect
	try:
		conn=psycopg2.connect("dbname='slope_db' user='postgres' host='localhost' password='p@ssw0rd'")
		print('database connected!!'.encode('utf-8').decode('utf-8')) 
	except:
		print('I am unable to connect to the database'.encode('utf-8').decode('utf-8')) 
		conn.close()
	
	#then we create a cursor to connect
	cur=conn.cursor()
	
	#now we execute a query
	cur.execute("INSERT INTO tag_data (id, date, data) VALUES (2, '2015-01-08 17:16:00', 'prueba introducir datos desde python')")

	#make changes persistent
	conn.commit()
	
	# and here we close the db connection
	cur.close()
	conn.close()

#main loop 
# if __name__  works ok in a direct execution. However, if the file is executed from another module, it is not executed
# that allows the other module to use de defined functions in this file without problems 
if __name__== '__main__':	
	#insertData()
	showDatabase() 
