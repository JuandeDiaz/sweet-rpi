# 08 ene 2015
# aim: to test Tkinter package

# imports
from tkinter import *

# Initializing elements
# Set Display sizes
WINDOW_W=500
WINDOW_H=100


# function to send and receive a command via TCP
def createDisplay():
	global tk	 
	tk=Tk()		# Creation of the main window, which will inclulde all elements    
	
	# Add Canvas Area, ready for drawing on	
	canvas = Canvas(tk, width=WINDOW_H, height=WINDOW_H)
	canvas.pack()	#pack is to draw it
	
	#Add button
	btn=Button(tk, text="Exit", command = terminate)
	btn.pack()
	
	#Start the main loop
	tk.mainloop()
	
def terminate():
	global tk
	tk.destroy()


#main loop 
# if __name__  works ok in a direct execution. However, if the file is executed from another module, it is not executed
# that allows the other module to use de defined functions in this file without problems 
if __name__== '__main__':	
	createDisplay()
	 
