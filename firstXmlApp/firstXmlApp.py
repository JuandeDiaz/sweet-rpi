# 14 ene 2015
# aim: to test XML usage

# imports
from tkinter import *
import xml.etree.ElementTree as ET

# Initializing elements

#  main function to create the display
def createDisplay():
	
	# create root window that will include all elements
	global root #we declare it global to be able to control it outside the loop
	root= Tk()	 
	root.wm_title('XML generator')	#title of the main window   
	root.config(background = '#FFFFFF')
	
	#Left frame and its contents
	leftFrame=Frame(root, width=200, height=600)
	leftFrame.grid(row=0, column=0, padx=10, pady=2)
	
	Label(leftFrame, text="Name:").grid(row=0, column=0, padx=10, pady=2)
	global e1
	e1=Entry(leftFrame)
	e1.grid(row=0, column=1, padx=10, pady=2)
	
	Label(leftFrame, text="Surname:").grid(row=1, column=0, padx=10, pady=2)
	global e2
	e2=Entry(leftFrame)
	e2.grid(row=1, column=1, padx=10, pady=2)
	
	Label(leftFrame, text="Phone:").grid(row=2, column=0, padx=10, pady=2)
	global e3
	e3=Entry(leftFrame)
	e3.grid(row=2, column=1, padx=10, pady=2)

	Label(leftFrame, text="--------------").grid(row=3, column=0, padx=10, pady=20)
	
	Label(leftFrame, text="Name:").grid(row=4, column=0, padx=10, pady=2)
	global e4
	e4=Entry(leftFrame)
	e4.grid(row=4, column=1, padx=10, pady=2)
	
	Label(leftFrame, text="Surname:").grid(row=5, column=0, padx=10, pady=2)
	global e5
	e5=Entry(leftFrame)
	e5.grid(row=5, column=1, padx=10, pady=2)
	
	Label(leftFrame, text="Phone:").grid(row=6, column=0, padx=10, pady=2)
	global e6
	e6=Entry(leftFrame)
	e6.grid(row=6, column=1, padx=10, pady=2)	
	
	# Right Frame and its contents
	rightFrame=Frame(root, width=200, height=600)
	rightFrame.grid(row=0, column=1, padx=10, pady=2)
	
	statusFrame=Frame(rightFrame, width=200, height=200)
	statusFrame.grid(row=0, column=0, padx=10, pady=2)
	
	scrollbar =Scrollbar(statusFrame)
	scrollbar.pack(side=RIGHT, fill=Y)
		
	global textLog
	textLog = Text(statusFrame, wrap=WORD, yscrollcommand=scrollbar.set, width=40, height=11)
	textLog.insert(END, "Welcome to the Xml Generator Tkinter Python software\n")	
	textLog.pack()
	
	btnFrame=Frame(rightFrame, width=200, height=200)
	btnFrame.grid(row=1, column=0, padx=10, pady=2)
		
	genXML=Button(btnFrame, text='Generate XML', command=generateXmlFile)
	genXML.grid(row=0, column=0, padx=10, pady=2)

	loadXML=Button(btnFrame, text='Load XML', command=loadXmlFile)
	loadXML.grid(row=0, column=1, padx=10, pady=2)

	exitBtn=Button(btnFrame, text='Exit', command=terminate)
	exitBtn.grid(row=0, column=2, padx=10, pady=2)
	
	#Start the main loop
	root.mainloop()			
		
def terminate():
	root.destroy()

def generateXmlFile():
	
	config=ET.Element("config")
	
	user1=ET.SubElement(config, "user")	
	name1=ET.SubElement(user1,"name")
	name1.text=(e1.get())		
	surname1=ET.SubElement(user1,"surname")
	surname1.text=(e2.get())	
	phone1=ET.SubElement(user1,"phone")
	phone1.text=(e3.get())
	
	user2=ET.SubElement(config, "user")	
	name2=ET.SubElement(user2,"name")
	name2.text=(e4.get())	
	surname2=ET.SubElement(user2,"surname")
	surname2.text=(e5.get())	
	phone2=ET.SubElement(user2,"phone")
	phone2.text=(e6.get())
	
	tree =ET.ElementTree(config)
	tree.write("config.xml")
	
	textLog.insert(END, "Xml file generated succcessfully\n")
	textLog.yview(END)  #to keep the last text always visible	
	
			
def loadXmlFile():
	#here we try to connecto to the xml file
	try:
		textLog.insert(END, "Trying to get file\n")	
		tree=ET.parse('config.xml')
		root=tree.getroot()
		textLog.insert(END, "File found\n")	
	except:	
		textLog.insert(END, "File not found\n")
	
	
	e1.delete(0,END)			#first we clear the field
	if not root[0][0].text:		#empty trings give error, so we identify first if the string is empty
		e1.insert(0,'')			# if it is empty, we introduce an empty value
	else:	
		texto=root[0][0].text	#if it is not empty		
		e1.insert(0,texto)		#we introduce the text

	e2.delete(0,END)
	if not root[0][1].text:
		e2.insert(0,'')
	else:	
		texto=root[0][1].text			
		e2.insert(0,texto)
	
	e3.delete(0,END)
	if not root[0][2].text:
		e3.insert(0,'')
	else:	
		texto=root[0][2].text			
		e3.insert(0,texto)	
	
	e4.delete(0,END)
	if not root[1][0].text:
		e4.insert(0,'')
	else:	
		texto=root[1][0].text			
		e4.insert(0,texto)	
	
	e5.delete(0,END)
	if not root[1][1].text:
		e5.insert(0,'')
	else:	
		texto=root[1][1].text			
		e5.insert(0,texto)		

	e6.delete(0,END)
	if not root[1][2].text:
		e6.insert(0,'')
	else:	
		texto=root[1][2].text			
		e6.insert(0,texto)				
	
	textLog.insert(END, "Xml file loaded successfully\n")
	textLog.yview(END)  #to keep the last text always visible

#main loop 
# if __name__  works ok in a direct execution. However, if the file is executed from another module, it is not executed
# that allows the other module to use de defined functions in this file without problems 
if __name__== '__main__':	
	createDisplay()
	 
