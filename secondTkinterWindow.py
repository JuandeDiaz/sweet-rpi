# 08 ene 2015
# aim: to test Tkinter package

# imports
from tkinter import *

# Initializing elements


# function to draw the red circle
def redCircle():
	circleCanvas.create_oval(20,20,80,80, width=0, fill='red')
	colorLog.insert(0.0, "Red\n")

def yelCircle():
	circleCanvas.create_oval(20,20,80,80, width=0, fill='yellow')
	colorLog.insert(0.0, "Yellow\n")

def grnCircle():
	circleCanvas.create_oval(20,20,80,80, width=0, fill='green')
	colorLog.insert(0.0, "Green\n")
	

#  main function to create the display
def createDisplay():
	
	# create root window that will include all elements
	global root 
	root= Tk()	 
	root.wm_title('Este es el titulo')	#title of the main window   
	root.config(background = '#FFFFFF')
	
	#Left frame and its contents
	leftFrame=Frame(root, width=200, height=600)
	leftFrame.grid(row=0, column=0, padx=10, pady=2)
	
	Label(leftFrame, text="Instructions:").grid(row=0, column=0, padx=10, pady=2)
	
	Instruct= Label(leftFrame, text="1\n2\n3\n4\n5\n6\n7\n8\n9\n")
	Instruct.grid(row=1, column=0, padx=10, pady=2)
	
	try:
		imageEx=Photoimage(file='image.gif')
		Label(leftFrame, image=imageEx).grid(row=2, column=0, padx=10, pady=2)
	
	except:
		print("Image not found")
	
	
	# Right Frame and its contents
	rightFrame=Frame(root, width=200, height=600)
	rightFrame.grid(row=0, column=1, padx=10, pady=2)
	
	global circleCanvas
	circleCanvas=Canvas(rightFrame, width=100, height=100, bg='white')
	circleCanvas.grid(row=0, column=0, padx=10, pady=2)	
	
	btnFrame=Frame(rightFrame, width=200, height=200)
	btnFrame.grid(row=1, column=0, padx=10, pady=2)
	
	redBtn=Button(btnFrame, text='Red', command=redCircle)
	redBtn.grid(row=0, column=0, padx=10, pady=2)
		
	yelBtn=Button(btnFrame, text='Yellow', command=yelCircle)
	yelBtn.grid(row=0, column=1, padx=10, pady=2)
	
	grnBtn=Button(btnFrame, text='Green', command=grnCircle)
	grnBtn.grid(row=0, column=2, padx=10, pady=2)
	
	global colorLog
	colorLog=Text(rightFrame, width=30, height=10, takefocus=0)
	colorLog.grid(row=2, column=0, padx=10, pady=2)
	
	exitBtn=Button(rightFrame, text='Exit', command=terminate)
	exitBtn.grid(row=3, column=0, padx=10, pady=2)
	
	#Start the main loop
	root.mainloop()
	
def terminate():
	global root
	root.destroy()


#main loop 
# if __name__  works ok in a direct execution. However, if the file is executed from another module, it is not executed
# that allows the other module to use de defined functions in this file without problems 
if __name__== '__main__':	
	createDisplay()
	 
