# 07 abr 2015
# aim: retrieve data from GPS BU-353S4

# imports
import os
import gps3
import threading
import time

# Initializing elements

# Clase que será actualizada por el hilo del GPS
class gpsClase():	
	lastLatitude ='nothing received'	
	lastLongitude ='nothing received'		
	lastDatetime ='nothing received'	
	lastAltitude ='nothing received'	
	lastSpeed ='nothing received'	
	
# método que siempre estará en marcha y actualizando el objeto miGps
def metodoGpsParaThread():
	the_connection=gps3.GPSDSocket()
	the_fix=gps3.Fix()

	while 1:
		try:
			print('antes esperar'.encode('utf-8').decode('utf-8')) 
				
			for new_data in the_connection:
			
				if new_data:
					the_fix.refresh(new_data) 
						
				if not isinstance(the_fix.TPV['speed'],str):
					miGps.lastSpeed = the_fix.TPV['speed']
					miGps.lastLatitude=the_fix.TPV['lat']
					miGps.lastLongitude=the_fix.TPV['lon']
					miGps.lastAltitude=the_fix.TPV['alt']				
					
					if isinstance(the_fix.TPV['track'], str):  # 'track' frequently is missing and returns as 'n/a'
						heading = the_fix.TPV['track']
					else:
						heading = round(the_fix.TPV['track'])  # and heading percision in hundreths is just clutter.
				else:
					pass

		except:
			print('exception'.encode('utf-8').decode('utf-8'))  

#main loop
 
miGps= gpsClase()

t=threading.Thread(target=metodoGpsParaThread)
t.start()

while 1:
	input("Pulsa intro para medir con el GPS")
	#print('sleeping'.encode('utf-8').decode('utf-8')) 
	#time.sleep(4)
	#print('awake'.encode('utf-8').decode('utf-8')) 
	texto = str(miGps.lastLatitude)
	print(texto.encode('utf-8').decode('utf-8')) 



