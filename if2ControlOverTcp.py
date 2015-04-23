# 29 dic 2014
# aim: to control the intermec if61 reader with tcp commands

# imports
import socket
import time

# Initializing elements
TCP_IP='192.168.0.222'
TCP_PORT=2189
BUFFER_SIZE=512
MESSAGE = 'briver\n'

# Open sequence
openList=[
'VER\n',   					# gets the version of the reader
'ATTRIB ANTS=1,2,3,4\n', 			# defines de sequence of antennas when reading
'ATTRIB TAGTYPE=EPCC1G2\n', # defines the tag to be read
'ATTRIB FIELDSTRENGTH=29DB,29DB,29DB,29DB\n', # define the RF power for each antenna
'ATTRIB RDTRIES=3\n', 		# number of attempts to read a tag before a response is returned
'ATTRIB RPTTIMEOUT=0\n', 	# sets delay in response
'ATTRIB IDTIMEOUT=4000\n', 	# sets maximum time attempting to read tags
'ATTRIB ANTTIMEOUT=0\n', 	# sets maximum time attempting to use antenna when reading tags
'ATTRIB IDTRIES=1\n', 		# sets number of times an attemp is made to read tags
'ATTRIB ANTTRIES=1\n', 		# sets number of times each antenna is used  for Read/Write
'ATTRIB WRTRIES=3\n', 		# sets number of times an attempt is made to Write Data
'ATTRIB LOCKTRIES=3\n', 	# sets number of times the lock algorithm is executed before answering
'ATTRIB SELTRIES=1\n', 		# sets number of times a group select is attempted
'ATTRIB UNSELTRIES=1\n', 	# sets number of times a group unselect is attempted
'ATTRIB INITTRIES=1\n', 	# sets initialization tries
'ATTRIB INITIALQ=1\n', 		# definite Q parameter value of the query command
'ATTRIB QUERYSEL=4\n', 		# define sel field for query commands
'ATTRIB QUERYTARGET=A\n', 	# define target field for query commands
'ATTRIB SESSION=1\n', 		# define session parameter
'ATTRIB LBTCHANNEL=7\n', 	# define channel for Listen-Before-Talk algorithm
'ATTRIB SCHEDULEOPT=1\n', 	# define how antennas are switched
'ATTRIB FIELDSEP=" "\n', 	# define separator in output
'ATTRIB BROADCASTSYNC=0\n', # enables or disables broadcast commands
'ATTRIB UTCTIME=1094\n', 	# value of UTCTime sent in BroadcastsSync commands
'ATTRIB TIMEOUTMODE=OFF\n', # define the usage of timeout and tries attributes
'ATTRIB NOTAGRPT=ON\n', 	# send a message when no tags are found
'ATTRIB IDREPORT=ON\n', 	# configure reader to send tag identifiers when a command is executed
'ATTRIB SCHEDOPT=1\n'] 		# same as SCHEDULEOPT?

# Close sequence
close1 = 'ATTRIB\n' # return current settings


# function to send and receive a command via TCP
def sendBriCommand(command):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#print('socket created'.encode('utf-8').decode('utf-8'))   
		s.connect((TCP_IP, TCP_PORT))
		#print('socket connected'.encode('utf-8').decode('utf-8'))   		
		s.send(command.encode('utf-8'))
		#print('message sent succesfuly'.encode('utf-8').decode('utf-8'))  
		response=s.recv(BUFFER_SIZE).decode()
		#print('message received succesffuly'.encode('utf-8').decode('utf-8')) 
		#print(data.encode('utf-8').decode('utf-8')) 
		s.close()     
		
	except:
		print("ha ocurrido una excepcion ejecutando el comando "+command.encode('utf-8').decode('utf-8'))  
		s.close()	
		response= "exception when doing "+ command
		
	finally:
		return response

def openingReader():
	for i in range(len(openList)):
		print(openList[i]
		)
		response = sendBriCommand(openList[i])
		print(response.encode('utf-8').decode('utf-8'))


#main loop 
#openingReader()
print("Reader initiated. Entering read mode...".encode('utf-8').decode('utf-8'))  
try:
	while True:
		response = sendBriCommand('ping\n')
		print(response.encode('utf-8').decode('utf-8'))
		time.sleep(2)
except KeyboardInterrupt:		# salta al pulsar contrl+C
	print('Interrupted'.encode('utf-8').decode('utf-8'))
	 
