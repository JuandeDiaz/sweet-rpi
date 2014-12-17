# 17 dic 2014
# aim: use a swich to change the LED status

# imports
import RPi.GPIO as GPIO
import time

# Initializing elements
LED = 4
SWITCH = 27

# Configuration of GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)   	# definimos el GPIO 4 como salida
GPIO.setup(SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Here a function is defined
def switchingTime():
	print('Iniciamos la ejecucion'.encode('utf-8').decode('utf-8')) # encode-decode is for avoid error when printing into the lxterminal
	while True:
		
		input_state=GPIO.input(SWITCH)
		if input_state == True:
			GPIO.output(LED, True)		# turn on GPIO 4
		else:
			GPIO.output(LED, False) 	# turn off GPIO 4
			
		time.sleep(0.05)				# slight delay to avoid debouncing
				

	print('Ejecucion finalizada'.encode('utf-8').decode('utf-8'))
	GPIO.cleanup()	#clean GPIO
	

# Call the function
try:
        switchingTime()

# exception that happens when the user presses CTRL+C
except KeyboardInterrupt:
	print("CTRL+C was pressed")
	
# all other exceptions
except:
        print("Ha habido un error y ha saltado la excepcion".encode('utf-8').decode('utf-8'))

finally:        
        GPIO.cleanup()	# to leave the GPIO free for future use
        
