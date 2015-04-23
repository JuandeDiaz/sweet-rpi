# 09 mar 2015
# aim: retrieve data from GPS BU-353S4

# imports
import os
import gps3

# Initializing elements

# Here a function is defined
def measureGps():	

	the_connection=gps3.GPSDSocket()
	the_fix=gps3.Fix()
	
	while 1:
		input("Pulsa intro para medir con el GPS")
		
		try:
			for new_data in the_connection:
				
				if new_data:
					the_fix.refresh(new_data)
					#print(new_data)
				
				if not isinstance(the_fix.TPV['speed'],str):
					print('Interrupted'.encode('utf-8').decode('utf-8'))
					speed = the_fix.TPV['speed']
					latitude=the_fix.TPV['lat']
					longitude=the_fix.TPV['lon']
					altitude=the_fix.TPV['alt']				
					texto="latitud = "+str(latitude)+ "; longitud =" +str(longitude)
					print(texto.encode('utf-8').decode('utf-8'))
					
					if isinstance(the_fix.TPV['track'], str):  # 'track' frequently is missing and returns as 'n/a'
						heading = the_fix.TPV['track']
					else:
						heading = round(the_fix.TPV['track'])  # and heading percision in hundreths is just clutter.
				else:
					pass
					
		except:
			print("ha ocurrido una excepcion".encode('utf-8').decode('utf-8'))  	
		
		
	#try:
		#for new_data in the_connection:
			#input("Pulsa intro para medir con el GPS")		
			
			#if new_data:
				#the_fix.refresh(new_data)
				#print(new_data)
			
			#if not isinstance(the_fix.TPV['lat'],str):
				#speed = the_fix.TPV['speed']
				#latitude=the_fix.TPV['lat']
				#longitude=the_fix.TPV['lon']
				#altitude=the_fix.TPV['alt']				
				#texto="latitud = "+str(latitude)+ "; longitud =" +str(longitude)
				#print(texto)
	#except:
		#print("ha ocurrido una excepcion".encode('utf-8').decode('utf-8'))  				
	 

#main loop
measureGps()	



