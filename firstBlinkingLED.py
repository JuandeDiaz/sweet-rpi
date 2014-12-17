# 17 dic 2014
# test archive to make the LED blink in the raspberry pi

# imports
import RPi.GPIO as GPIO
import time

# Module level constants
LED = 4

# Configuration of GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)   	# definimos el GPIO 4 como salida

# Definimos una funcion
def blink():
	prueba='Ejecucion_iniciada'
	print(prueba.encode('utf-8').decode('utf-8')) # encode-decode is for avoid error when printing into the lxterminal
	iteracion = 0
	while iteracion < 60:
		GPIO.output(LED, True)	# enciendo GPIO 4
		time.sleep(1)			# espero 1 segundo
		GPIO.output(LED, False) # apago GPIO 4
		time.sleep(1)			# espero 1 segundo
		iteracion = iteracion + 2	# add 2 because I've made two blinks
		print ('Iteracion'.encode('utf-8').decode('utf-8'))
	print('Ejecucion finalizada'.encode('utf-8').decode('utf-8'))
	GPIO.cleanup()	#clean GPIO
	
blink()

# Call the function
try:
        blink()
except:
        print("Ha habido un error".encode('utf-8').decode('utf-8'))
        GPIO.cleanup()	# to leave the GPIO free for future use
