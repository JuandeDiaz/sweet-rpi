# 18 dic 2014
# aim: to send a tcp command to the intermec if61

# imports
import socket
import time

# Initializing elements
TCP_IP='192.168.0.251'
TCP_PORT=2189
BUFFER_SIZE=512
MESSAGE = 'briver\n'

# con estos datos si que se envia y recibe
#TCP_IP='www.google.com'
#TCP_PORT=80
#MESSAGE = "GET /HTTP/1.1\r\n\r\n"


# Here a function is defined
def sendBriCommand():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print('socket created'.encode('utf-8').decode('utf-8')) 
	 
	s.connect((TCP_IP, TCP_PORT))
	print('socket connected'.encode('utf-8').decode('utf-8'))   
	
	s.send(MESSAGE.encode('utf-8'))
	print('message sent succesfuly'.encode('utf-8').decode('utf-8')) 
	 
	#ATENCION se necesita un poco de tiempo para recibir todo la respuesta del reader
	#sin esperar la respuesta se corta
	time.sleep(1)
	data=s.recv(BUFFER_SIZE).decode()
	print('message received succesffuly'.encode('utf-8').decode('utf-8')) 
	print(data.encode('utf-8').decode('utf-8')) 
	s.close()       

#main loop
try:
	sendBriCommand()
	
except:
	print("ha ocurrido una excepcion".encode('utf-8').decode('utf-8'))  
	s.close()	


