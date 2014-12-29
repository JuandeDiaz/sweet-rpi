# 18 dic 2014
# aim: to send a tcp command to the intermec if61

# imports
import picamera
import time

# Initializing elements


# Here a function is defined
def makePhoto():	
	camera = picamera.PiCamera()
	print('objeto picamera creado'.encode('utf-8').decode('utf-8')) 
	time.sleep(40)
	camera.capture('image.jpg')
	print('captura realizada'.encode('utf-8').decode('utf-8')) 


# Here a function is defined
# WARNING: video playing do not work over vnc, direct connection needs to be done
def makeVideo():	
	camera = picamera.PiCamera()
	print('objeto picamera creado'.encode('utf-8').decode('utf-8')) 
	camera.start_recording('video.h264')
	print('grabacion iniciada'.encode('utf-8').decode('utf-8')) 
	time.sleep(5)
	camera.stop_recording()
	print('grabacion finalizada'.encode('utf-8').decode('utf-8')) 

#main loop
try:
	#makeVideo()
	makePhoto()	
except:
	print("ha ocurrido una excepcion".encode('utf-8').decode('utf-8'))  


