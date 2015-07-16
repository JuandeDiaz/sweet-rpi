# started on 04 feb 2015
# SLOPE project
# Task 3.5 
# aim: read RFID and GPS, store it in DB and transmit it via GPRS
# NOTE: app created as a class. This way you do not need global variables, nor to pass arguments 
# NOTE: self is used to make the variable global inside the class
# NOTE: if we do not use self, variables are ceated locally and cannot be shared between methods

# imports
import tkinter as tk				# main library to develop the gui
import xml.etree.ElementTree as ET	# to work with xml files / structures
import socket						# to use sockets to connect to the RFID reader
import datetime						# to work with dates
import psycopg2						# to create a postgress connection
import threading 					# to allow threads
import os
import gps3							# to work with GPS module
import time
import queue						# to allow queues, used to communicate between threads
from PIL import Image, ImageTk		# to use images in the gui
import requests						# to communicate via http with SLOPE MHG platform

"""structure for database tables"""
class databaseEntry:
	

	"""Constructor and setting variables"""
	def __init__(self):
		self.id=0
		self.truckId=0
		self.time=datetime.datetime.now()
		self.longitude=0
		self.latitude=0
		self.altitude=0
		self.speed=0
		self.EPCData='H111122223333AAAA'
		self.isSent=False
		self.comments=''



"""structure for data received from GPS"""
class gpsPoint:


	def __init__(self):
		self.Speed='notYetReceived'
		self.Latitude='notYetReceived'
		self.Longitude='notYetReceived'
		self.Altitude='notYetReceived'
		self.Time='notYetReceived'
	
	
	
"""main class to create the UI"""
class Gui():	
	
	
	"""Variables definition"""	
	
	#Status variables
	isThereGps = False
	isThereGprs = False
	isThereRfidReader =False
	isTruckOn =True	
	
	TIME_NEXT_MEASUREMENT=datetime.datetime.now()
	
	commandList=['']
	numCommands=[0, 0]			#[total commands, next command to be processed]
	
	#create the queue
	myGpsQueue =queue.Queue()
	myRfidQueue =queue.Queue()
		
	#create the Gps point to store last position
	myLastGpsPoint=gpsPoint()
	
		
	#RFID Reader Variables
	TCP_IP_RFID_READER='0.0.0.0' #ATTENTION: Change IP from the configuration window
	TCP_PORT_RFID_READER=2189
	BUFFER_SIZE_RFID_READER=512	
	FREQ_READ_RFID = 60
	FREQ_ACCESS_PLATF = 600
	
	#Other Variables
	TRUCK_ID = '000'
	COMMENTS = 'default comment'
		
	#Reader Attributes
	ATTRIB_ANTS='1,2,3,4'		# 'ATTRIB ANTS=1,2,3,4\n' defines de sequence of antennas when reading
	ATTRIB_TAGTYPE='EPCC1G2'	# 'ATTRIB TAGTYPE=EPCC1G2\n' defines the tag to be read
	ATTRIB_FIELDSTRENGTH='29DB,29DB,29DB,29DB'	# 'ATTRIB FIELDSTRENGTH=29DB,29DB,29DB,29DB\n' define the RF power for each antenna
	ATTRIB_RDTRIES='3'			# 'ATTRIB RDTRIES=3\n' number of attempts to read a tag before a response is returned
	ATTRIB_RPTTIMEOUT='0'		# 'ATTRIB RPTTIMEOUT=0\n' sets delay in response
	ATTRIB_IDTIMEOUT='4000'		# 'ATTRIB IDTIMEOUT=4000\n' sets maximum time attempting to read tags
	ATTRIB_ANTTIMEOUT='0'		# 'ATTRIB ANTTIMEOUT=0\n' sets maximum time attempting to use antenna when reading tags
	ATTRIB_IDTRIES='1'			# 'ATTRIB IDTRIES=1\n' sets number of times an attemp is made to read tags
	ATTRIB_ANTTRIES='1'			# 'ATTRIB ANTTRIES=1\n' sets number of times each antenna is used  for Read/Write
	ATTRIB_WRTRIES='3'			# 'ATTRIB WRTRIES=3\n' sets number of times an attempt is made to Write Data
	ATTRIB_LOCKTRIES='3'		# 'ATTRIB LOCKTRIES=3\n' sets number of times the lock algorithm is executed before answering
	ATTRIB_SELTRIES='1'			# 'ATTRIB SELTRIES=1\n' sets number of times a group select is attempted
	ATTRIB_UNSELTRIES='1'		# 'ATTRIB UNSELTRIES=1\n' sets number of times a group unselect is attempted
	ATTRIB_INITTRIES='1'		# 'ATTRIB INITTRIES=1\n' sets initialization tries
	ATTRIB_INITIALQ='1'			# 'ATTRIB INITIALQ=1\n' definite Q parameter value of the query command
	ATTRIB_QUERYSEL='4'			# 'ATTRIB QUERYSEL=4\n' define sel field for query commands
	ATTRIB_QUERYTARGET='A'		# 'ATTRIB QUERYTARGET=A\n' define target field for query commands	
	ATTRIB_SESSION='1'			# 'ATTRIB SESSION=1\n' define session parameter
	ATTRIB_LBTCHANNEL='7'		# 'ATTRIB LBTCHANNEL=7\n' define channel for Listen-Before-Talk algorithm
	ATTRIB_SCHEDULEOPT='1'		# 'ATTRIB SCHEDULEOPT=1\n' define how antennas are switched
	ATTRIB_FIELDSEP=' '			# 'ATTRIB FIELDSEP=" "\n' define separator in output	
	ATTRIB_BROADCASTSYNC='0'	# 'ATTRIB BROADCASTSYNC=0\n' enables or disables broadcast commands
	ATTRIB_UTCTIME='1094'		# 'ATTRIB UTCTIME=1094\n' value of UTCTime sent in BroadcastsSync commands
	ATTRIB_TIMEOUTMODE='OFF'	# 'ATTRIB TIMEOUTMODE=OFF\n' define the usage of timeout and tries attributes
	ATTRIB_NOTAGRPT='ON'		# 'ATTRIB NOTAGRPT=ON\n' send a message when no tags are found	
	ATTRIB_IDREPORT='ON'		# 'ATTRIB IDREPORT=ON\n' configure reader to send tag identifiers when a command is executed
	ATTRIB_SCHEDOPT='1'			# 'ATTRIB SCHEDOPT=1\n' same as SCHEDULEOPT	
		
	
	"""	Initial code """
	def __init__(self, master):
		
		
		self.root = master
		
		# loading the main gui widgets: buttons, texts, testLog
		self.loadMainGui()
		
		# Loading xml config file, updating internal variables
		self.loadXmlFile()		
		
		# Starts periodic method 
		self.root.after(500, self.updateMe)
	
		
	""" loading the main gui widgets: buttons, texts, testLog """
	def loadMainGui(self):
	
		#main window 
		self.root.wm_title('iTruck Main Window')	#title of the main window 
		
		#topFrame
		topFrame=tk.Frame(self.root)		
		topFrame.grid(row=0, column=0, padx=10, pady=2)	
		
		imageLogoUe=Image.open("img/logo_ue.jpg")
		imageLogoUe=imageLogoUe.resize((83, 50), Image.ANTIALIAS)
		imgLogoUe=ImageTk.PhotoImage(imageLogoUe)		
			
		lblLogoUe=tk.Label(topFrame, image=imgLogoUe)
		lblLogoUe.image=imgLogoUe
		lblLogoUe.grid(row=0, column=0, padx=10, pady=10)

		imageLogoSlope=Image.open("img/logo_slope.png")
		imageLogoSlope=imageLogoSlope.resize((62, 50))
		imgLogoSlope=ImageTk.PhotoImage(imageLogoSlope)		
			
		lblLogoUe=tk.Label(topFrame, image=imgLogoSlope)
		lblLogoUe.image=imgLogoSlope
		lblLogoUe.grid(row=0, column=1, padx=10, pady=10)
		
		#separator
		sep1=tk.Frame(self.root, height=2, width=200, borderwidth=2, relief=tk.RAISED)		
		sep1.grid(row=1, column=0, sticky=tk.W+tk.E, padx=10, pady=4)		
			
		#Left frame 
		leftFrame=tk.Frame(self.root)
		leftFrame.grid(row=2, column=0, padx=10, pady=2)
		
		#indicators Frame
		indicatorsFrame=tk.Frame(leftFrame)
		indicatorsFrame.grid(row=0, column=0, padx=0) 

		imageLedRed=Image.open("img/led_red.png")
		imageLedRed=imageLedRed.resize((20, 20))
		self.imgLedRed=ImageTk.PhotoImage(imageLedRed)	
		
		imageLedGreen=Image.open("img/led_green.png")
		imageLedGreen=imageLedGreen.resize((20, 20))
		self.imgLedGreen=ImageTk.PhotoImage(imageLedGreen)	
	
		lbl1=tk.Label(indicatorsFrame, text="Running:").grid(row=0, column=0, padx=0, pady=2, sticky=tk.W)			
		self.lblLedRunning=tk.Label(indicatorsFrame, image=self.imgLedRed)
		self.lblLedRunning.image=self.imgLedRed
		self.lblLedRunning.grid(row=0, column=1, padx=10, pady=2, sticky=tk.E)	

		lbl2=tk.Label(indicatorsFrame, text="RFID reader:").grid(row=1, column=0, padx=0, pady=2, sticky=tk.W)				
		self.lblLedRfid=tk.Label(indicatorsFrame, image=self.imgLedRed)
		self.lblLedRfid.image=self.imgLedRed
		self.lblLedRfid.grid(row=1, column=1, padx=10, pady=2)	
						
		lbl3=tk.Label(indicatorsFrame, text="GPS connection:").grid(row=2, column=0, padx=0, pady=2, sticky=tk.W)		
		self.lblLedGps=tk.Label(indicatorsFrame, image=self.imgLedRed)
		self.lblLedGps.image=self.imgLedRed
		self.lblLedGps.grid(row=2, column=1, padx=10, pady=2)
			
		lbl4=tk.Label(indicatorsFrame, text="GPRS connection:").grid(row=3, column=0, padx=0, pady=2, sticky=tk.W)
		self.lblLedGprs=tk.Label(indicatorsFrame, image=self.imgLedRed)
		self.lblLedGprs.image=self.imgLedRed
		self.lblLedGprs.grid(row=3, column=1, padx=10, pady=2)
				
		#separator
		sep1=tk.Frame(leftFrame, height=2, width=100, borderwidth=2, relief=tk.RAISED)		
		sep1.grid(row=1, sticky=tk.W+tk.E, padx=10, pady=4)
		
		#action Frame		
		actionFrame=tk.Frame(leftFrame)
		actionFrame.grid(row=2, column=0, pady=10) 
		
		self.imageStop=Image.open("img/stop.png")
		self.imgStop=ImageTk.PhotoImage(self.imageStop)	
		self.imagePlay=Image.open("img/play.png")
		self.imgPlay=ImageTk.PhotoImage(self.imagePlay)			
					
		self.btnPlayStop=tk.Button(actionFrame, image=self.imgStop, command=self.btnPlayStop_click)
		self.btnPlayStop.image=self.imgStop
		self.btnPlayStop.grid(row=1, column=0, padx=10, pady=2)			

		imageTest=Image.open("img/aid-kit.png")
		imgTest=ImageTk.PhotoImage(imageTest)				
		btnTest=tk.Button(actionFrame, image=imgTest, command=self.createTestWindow)
		btnTest.image=imgTest
		btnTest.grid(row=1, column=1, padx=10, pady=2)			
		
		imageConfig=Image.open("img/wrench.png")
		imgConfig=ImageTk.PhotoImage(imageConfig)				
		btnConfig=tk.Button(actionFrame, image=imgConfig, command=self.createConfigureWindow)
		btnConfig.image=imgConfig
		btnConfig.grid(row=1, column=2, padx=10, pady=2)	

		imageExit=Image.open("img/exit.png")
		imgExit=ImageTk.PhotoImage(imageExit)				
		btnExit=tk.Button(actionFrame, image=imgExit, command=self.exitBtn_click)
		btnExit.image=imgExit
		btnExit.grid(row=1, column=3, padx=10, pady=2)	
		
		# Right Frame and its contents
		rightFrame=tk.Frame(self.root, width=200, height=600)
		rightFrame.grid(row=0, column=1, rowspan=4, padx=10, pady=10)
		
		statusFrame=tk.Frame(rightFrame, width=200, height=200)
		statusFrame.grid(row=0, column=0, padx=10, pady=2)
		
		scrollbar=tk.Scrollbar(statusFrame)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		#testLog
		self.mainLog = tk.Text(statusFrame, wrap=tk.WORD, yscrollcommand=scrollbar.set, width=40, height=16)
		self.mainLog.insert(tk.END, "Welcome to the iTruck app\n")	
		self.mainLog.insert(tk.END, "SLOPE Project \n")	
		self.mainLog.insert(tk.END, "Version v1 \n")	
		self.mainLog.insert(tk.END, "--------------------\n")	
		currentTime = str(datetime.datetime.now().strftime('%x %X'))
		self.mainLog.insert(tk.END, "Current date: "+currentTime+"\n")
		self.mainLog.pack()
		scrollbar.config(command=self.mainLog.yview)
	
		
	"""updates internal variables with values stored in XML file """
	def loadXmlFile(self):
		
		#here we try to connect to the xml file		
		try:
			tree=ET.parse('config.xml')
			XMLroot=tree.getroot()
			self.mainLog.insert(tk.END, "Config file found\n")	
		except:	
			self.mainLog.insert(tk.END, "Config file not found\n")

		#Main Congiguration Info		
		if not XMLroot[0][0].text:		#empty trings give error, so we identify first if the string is empty
			self.TCP_IP_RFID_READER=''
		else:	
			self.TCP_IP_RFID_READER=XMLroot[0][0].text	#if it is not empty				

		if not XMLroot[0][1].text:		#empty trings give error, so we identify first if the string is empty
			self.TCP_PORT_RFID_READER=0
		else:	
			self.TCP_PORT_RFID_READER=int(XMLroot[0][1].text)	#if it is not empty		

		if not XMLroot[0][2].text:		#empty trings give error, so we identify first if the string is empty
			self.BUFFER_SIZE_RFID_READER=0
		else:	
			self.BUFFER_SIZE_RFID_READER=int(XMLroot[0][2].text)	#if it is not empty		

		if not XMLroot[0][3].text:		#empty trings give error, so we identify first if the string is empty
			self.FREQ_READ_RFID=0
		else:	
			self.FREQ_READ_RFID=int(XMLroot[0][3].text)	#if it is not empty	
		
		if not XMLroot[0][4].text:		#empty trings give error, so we identify first if the string is empty
			self.FREQ_ACCESS_PLATF=0
		else:	
			self.FREQ_ACCESS_PLATF=int(XMLroot[0][4].text)	#if it is not empty	

		if not XMLroot[0][5].text:		#empty trings give error, so we identify first if the string is empty
			self.TRUCK_ID=0
		else:	
			self.TRUCK_ID=int(XMLroot[0][5].text)	#if it is not empty	

		if not XMLroot[0][6].text:		#empty trings give error, so we identify first if the string is empty
			self.COMMENTS=0
		else:	
			self.COMMENTS=XMLroot[0][6].text	#if it is not empty	

		#RFID Congiguration Info - BRI Commands
		if not XMLroot[1][0].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_ANTS=''
		else:	
			self.ATTRIB_ANTS=XMLroot[1][0].text	#if it is not empty	

		if not XMLroot[1][1].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_TAGTYPE=''
		else:	
			self.ATTRIB_TAGTYPE=XMLroot[1][1].text	#if it is not empty	
			
		if not XMLroot[1][2].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_FIELDSTRENGTH=''
		else:	
			self.ATTRIB_FIELDSTRENGTH=XMLroot[1][2].text	#if it is not empty	

		if not XMLroot[1][3].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_RDTRIES=''
		else:	
			self.ATTRIB_RDTRIES=XMLroot[1][3].text	#if it is not empty	

		if not XMLroot[1][4].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_RPTTIMEOUT=''
		else:	
			self.ATTRIB_RPTTIMEOUT=XMLroot[1][4].text	#if it is not empty	
			
		if not XMLroot[1][5].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_IDTIMEOUT=''
		else:	
			self.ATTRIB_IDTIMEOUT=XMLroot[1][5].text	#if it is not empty	

		if not XMLroot[1][6].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_ANTTIMEOUT=''
		else:	
			self.ATTRIB_ANTTIMEOUT=XMLroot[1][6].text	#if it is not empty	

		if not XMLroot[1][7].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_IDTRIES=''
		else:	
			self.ATTRIB_IDTRIES=XMLroot[1][7].text	#if it is not empty	
			
		if not XMLroot[1][8].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_ANTTRIES=''
		else:	
			self.ATTRIB_ANTTRIES=XMLroot[1][8].text	#if it is not empty	

		if not XMLroot[1][9].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_WRTRIES=''
		else:	
			self.ATTRIB_WRTRIES=XMLroot[1][9].text	#if it is not empty	

		if not XMLroot[1][10].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_LOCKTRIES=''
		else:	
			self.ATTRIB_LOCKTRIES=XMLroot[1][10].text	#if it is not empty	
			
		if not XMLroot[1][11].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_SELTRIES=''
		else:	
			self.ATTRIB_SELTRIES=XMLroot[1][11].text	#if it is not empty	

		if not XMLroot[1][12].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_UNSELTRIES=''
		else:	
			self.ATTRIB_UNSELTRIES=XMLroot[1][12].text	#if it is not empty	

		if not XMLroot[1][13].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_INITTRIES=''
		else:	
			self.ATTRIB_INITTRIES=XMLroot[1][13].text	#if it is not empty	
			
		if not XMLroot[1][14].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_INITIALQ=''
		else:	
			self.ATTRIB_INITIALQ=XMLroot[1][14].text	#if it is not empty	

		if not XMLroot[1][15].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_QUERYSEL=''
		else:	
			self.ATTRIB_QUERYSEL=XMLroot[1][15].text	#if it is not empty	

		if not XMLroot[1][16].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_QUERYTARGET=''
		else:	
			self.ATTRIB_QUERYTARGET=XMLroot[1][16].text	#if it is not empty	
			
		if not XMLroot[1][17].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_SESSION=''
		else:	
			self.ATTRIB_SESSION=XMLroot[1][17].text	#if it is not empty	

		if not XMLroot[1][18].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_LBTCHANNEL=''
		else:	
			self.ATTRIB_LBTCHANNEL=XMLroot[1][18].text	#if it is not empty	

		if not XMLroot[1][19].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_SCHEDULEOPT=''
		else:	
			self.ATTRIB_SCHEDULEOPT=XMLroot[1][19].text	#if it is not empty	
			
		if not XMLroot[1][20].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_FIELDSEP=''
		else:	
			self.ATTRIB_FIELDSEP=XMLroot[1][20].text	#if it is not empty	

		if not XMLroot[1][21].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_BROADCASTSYNC=''
		else:	
			self.ATTRIB_BROADCASTSYNC=XMLroot[1][21].text	#if it is not empty	

		if not XMLroot[1][22].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_UTCTIME=''
		else:	
			self.ATTRIB_UTCTIME=XMLroot[1][22].text	#if it is not empty	
			
		if not XMLroot[1][23].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_TIMEOUTMODE=''
		else:	
			self.ATTRIB_TIMEOUTMODE=XMLroot[1][23].text	#if it is not empty	

		if not XMLroot[1][24].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_NOTAGRPT=''
		else:	
			self.ATTRIB_NOTAGRPT=XMLroot[1][24].text	#if it is not empty	

		if not XMLroot[1][25].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_IDREPORT=''
		else:	
			self.ATTRIB_IDREPORT=XMLroot[1][25].text	#if it is not empty	
			
		if not XMLroot[1][26].text:		#empty trings give error, so we identify first if the string is empty
			self.ATTRIB_SCHEDOPT=''
		else:	
			self.ATTRIB_SCHEDOPT=XMLroot[1][26].text	#if it is not empty	
		
		self.mainLog.insert(tk.END, "Xml file loaded successfully\n")
		self.mainLog.insert(tk.END, "--------------------\n")
		self.mainLog.yview(tk.END)  #to keep the last text always visible
			
		

	"""Updates main Window periodically: GPS, GPRS, RFID Reader Status, Queue data"""
	def updateMe(self):	
	
		#first we updated the RFID status
		
		self.isThereRfidReader =Worker2.isThereReader
	
		self.isThereGprs =Worker3.isThereGprs	
	
	
	
		# first we update the LEDs	
		if self.isTruckOn is True:			
			self.lblLedRunning.config(image=self.imgLedGreen)		
			self.btnPlayStop.config(image=self.imgStop)
		else:
			self.lblLedRunning.config(image=self.imgLedRed)			
			self.btnPlayStop.config(image=self.imgPlay)

		if self.isThereRfidReader is True:			
			self.lblLedRfid.config(image=self.imgLedGreen)	
		else:
			self.lblLedRfid.config(image=self.imgLedRed)	
									
		if self.isThereGps is True:			
			self.lblLedGps.config(image=self.imgLedGreen)
		else:
			self.lblLedGps.config(image=self.imgLedRed)
			
		if self.isThereGprs is True:			
			self.lblLedGprs.config(image=self.imgLedGreen)
		else:
			self.lblLedGprs.config(image=self.imgLedRed)
							
		# then we check for new data in the GPS queue
		while self.myGpsQueue.qsize():
			try: 
				newPoint=self.myGpsQueue.get(0)
				#Here we do something with the queued value
				
				self.myLastGpsPoint=newPoint
				
				self.isThereGps=True
			
				#self.mainLog.insert(tk.END, 'Time: ' + str(self.myLastGpsPoint.Time) + '\n')
				#self.mainLog.insert(tk.END, 'Latitude: ' + str(self.myLastGpsPoint.Latitude) + '\n')
				#self.mainLog.yview(tk.END)  #to keep the last text always visible
		
			except self.myGpsQueue.Empty:
				#self.mainLog.insert(tk.END, 'empty queue' + '\n')
				#self.mainLog.yview(tk.END)  #to keep the last text always visible
				pass
		
		
		#now we check for new data in the RFID queue 
		listPoints=[]
			
		while self.myRfidQueue.qsize():
	
			try:			
				#we create a point
				p = databaseEntry()			
				p.EPCData=self.myRfidQueue.get(0)
				p.latitude = self.myLastGpsPoint.Latitude
				p.longitude=self.myLastGpsPoint.Longitude
				p.altitude=self.myLastGpsPoint.Altitude
				p.time=self.myLastGpsPoint.Time
				p.speed=self.myLastGpsPoint.Speed
				p.truckId=self.TRUCK_ID
				p.comments=self.COMMENTS				
				
				#we add it to the list	of points
				listPoints.append(p)
									
			except self.myRfidQueue.Empty:
				pass

			
		if len(listPoints) >0:		
			self.mainLog.insert(tk.END, str(len(listPoints)) + ' points stored in the DB\n')
			self.mainLog.yview(tk.END)  #to keep the last text always visible				
		
		# For the number of points in the list, do:
		for i in range(len(listPoints)):
			p=listPoints.pop()
						
			if self.isThereGps:
				self.storePointInDb(p)
					
		#finally the task launches again itself after some time
		self.root.after(500, self.updateMe)


	"""Toogles running or stopped state"""
	def btnPlayStop_click(self):
		if self.isTruckOn is True:
			self.isTruckOn= False
			
			#then we update the Rfid worker values
			Worker2.updateValues(self.myRfidQueue, self.isTruckOn, self.FREQ_READ_RFID, self.TCP_IP_RFID_READER, self.TCP_PORT_RFID_READER, self.BUFFER_SIZE_RFID_READER)

		else:
			self.isTruckOn= True	
			
			#then we update the Rfid worker values
			Worker2.updateValues(self.myRfidQueue, self.isTruckOn, self.FREQ_READ_RFID, self.TCP_IP_RFID_READER, self.TCP_PORT_RFID_READER, self.BUFFER_SIZE_RFID_READER)
		

	"""launches a new window to test different elements"""
	def createTestWindow(self):
		
		#testFrame---MAIN FRAME
		testWindow=tk.Toplevel()
		testWindow.wm_title("Test Window") 
				
		#test Left Frame----MAIN LEFT FRAME
		testLeftFrame=tk.Frame(testWindow, width=200, height=200)
		testLeftFrame.grid(row=0, column=0, padx=10, pady=2)
				
		
		#top Left Frame
		topLeftFrame=tk.Frame(testLeftFrame)		
		topLeftFrame.grid(row=0, column=0, padx=0, pady=2)					
		
		lbl5=tk.Label(topLeftFrame, text="Testing RFID reader").grid(row=0, column=0, padx=10, pady=2, sticky=tk.W)
		
		lbl6=tk.Label(topLeftFrame, text="Enter BRI Command:").grid(row=1, column=0, padx=10, pady=2, sticky=tk.W)				
		self.eTestRfid=tk.Entry(topLeftFrame)
		self.eTestRfid.grid(row=1, column=1, padx=10, pady=2)				
		btnSendTestCommand=tk.Button(topLeftFrame, text='Send', width=8, command=self.btnSendTestCommand_click)
		btnSendTestCommand.grid(row=1, column=2, padx=10, pady=2)		

		lbl7=tk.Label(topLeftFrame, text="Load reader configuration:").grid(row=2, column=0, columnspan=2, padx=10, pady=2, sticky=tk.W)							
		btnReadTestCommand=tk.Button(topLeftFrame, text='Load', width=8, command=self.btnLoadTestCommand_click)
		btnReadTestCommand.grid(row=2, column=2, padx=10, pady=2)	

		lbl8=tk.Label(topLeftFrame, text="Read tags, RSSI, ANT:").grid(row=3, column=0, columnspan=2, padx=10, pady=2, sticky=tk.W)							
		btnReadTestCommand=tk.Button(topLeftFrame, text='Read', width=8, command=self.btnReadTestCommand_click)
		btnReadTestCommand.grid(row=3, column=2, padx=10, pady=2)	

		lbl9=tk.Label(topLeftFrame, text="Write data in EPC format:").grid(row=4, column=0, padx=10, pady=2, sticky=tk.W)				
		self.eTagData=tk.Entry(topLeftFrame)
		self.eTagData.grid(row=4, column=1, padx=10, pady=2)
		self.eTagData.delete(0, tk.END)
		self.eTagData.insert(0, "H000011112222AAAA")	#data format for EPC tags			
		btnWriteTestCommand=tk.Button(topLeftFrame, text='Write', width=8, command=self.btnWriteTestCommand_click)
		btnWriteTestCommand.grid(row=4, column=2, padx=10, pady=2)

		lbl10=tk.Label(topLeftFrame, text="Reset RFID module:").grid(row=5, column=0, columnspan=2, padx=10, pady=2, sticky=tk.W)							
		btnResetTestCommand=tk.Button(topLeftFrame, text='Reset', width=8, command=self.btnResetTestCommand_click)
		btnResetTestCommand.grid(row=5, column=2, padx=10, pady=2)	


		lbl11=tk.Label(topLeftFrame, text="Read and store tag in DB").grid(row=6, column=0, columnspan=2, padx=10, pady=2, sticky=tk.W)							
		btnStoreInDb=tk.Button(topLeftFrame, text='Store', width=8, command=self.btnStoreInDb_click)
		btnStoreInDb.grid(row=6, column=2, padx=10, pady=2)	
		
		lbl12=tk.Label(topLeftFrame, text="Read GPS Data").grid(row=7, column=0, columnspan=2, padx=10, pady=2, sticky=tk.W)							
		btnReadGpsData=tk.Button(topLeftFrame, text='Read GPS', width=8, command=self.btnReadGpsData_click)
		btnReadGpsData.grid(row=7, column=2, padx=10, pady=2)	
		
		lbl13=tk.Label(topLeftFrame, text="Try GPRS Connection").grid(row=8, column=0, columnspan=2, padx=10, pady=2, sticky=tk.W)							
		btnTestGprs=tk.Button(topLeftFrame, text='Test Gprs', width=8, command=self.btnTestGprs_click)
		btnTestGprs.grid(row=8, column=2, padx=10, pady=2)	

		#separator
		sep2=tk.Frame(testLeftFrame, height=2,  borderwidth=2, relief=tk.RAISED)		
		sep2.grid(row=1, column=0, sticky=tk.W+tk.E, padx=10, pady=4)
				
		#bottom Left Frame
		bottomLeftFrame=tk.Frame(testLeftFrame)
		bottomLeftFrame.grid(row=2, column=0) 
		
		imageLogoUe=Image.open("img/logo_ue.jpg")
		imageLogoUe=imageLogoUe.resize((58, 35), Image.ANTIALIAS)
		imgLogoUe=ImageTk.PhotoImage(imageLogoUe)		
			
		lblLogoUe=tk.Label(bottomLeftFrame, image=imgLogoUe)
		lblLogoUe.image=imgLogoUe
		lblLogoUe.grid(row=0, column=0, padx=10, pady=10)

		imageLogoSlope=Image.open("img/logo_slope.png")
		imageLogoSlope=imageLogoSlope.resize((43, 35))
		imgLogoSlope=ImageTk.PhotoImage(imageLogoSlope)		
			
		lblLogoUe=tk.Label(bottomLeftFrame, image=imgLogoSlope)
		lblLogoUe.image=imgLogoSlope
		lblLogoUe.grid(row=0, column=1, padx=10, pady=10)			

		saveLogButton=tk.Button(bottomLeftFrame, text='Save Log', width=8, height=2, command=self.saveLogButton_click)
		saveLogButton.grid(row=0, column=2, padx=10, pady=2)	
				
		imageExit=Image.open("img/exit.png")
		imgExit=ImageTk.PhotoImage(imageExit)
						
		btnExit=tk.Button(bottomLeftFrame, image=imgExit, command=testWindow.destroy)
		btnExit.image=imgExit
		btnExit.grid(row=0, column=3, padx=10, pady=2)	
		
		#test Right Frame
		testRightFrame=tk.Frame(testWindow, width=200, height=200)
		testRightFrame.grid(row=0, column=1, padx=10, pady=2)	
		
		testScrollbar=tk.Scrollbar(testRightFrame)
		testScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		
		#mainLog
		self.testLog = tk.Text(testRightFrame, wrap=tk.WORD, yscrollcommand=testScrollbar.set, width=40, height=16)
		self.testLog.insert(tk.END, "Welcome to the iTruck app\n")	
		self.testLog.insert(tk.END, "SLOPE Project \n")	
		self.testLog.insert(tk.END, "Version v1 \n")	
		self.testLog.insert(tk.END, "--------------------\n")	
		currentTime = str(datetime.datetime.now().strftime('%x %X'))
		self.testLog.insert(tk.END, "Current date: "+currentTime+"\n")
		self.testLog.pack()
		testScrollbar.config(command=self.testLog.yview)


	"""launches a new window to configure the RFID reader"""
	def createConfigureWindow(self):
				
		configWindow=tk.Toplevel()
		configWindow.wm_title("Configuration")	
		
		
		lbl0=tk.Label(configWindow, text="Configuration").grid(row=0, column=0, padx=10, pady=1)				

		separator=tk.Frame(configWindow, height=2, width=100, borderwidth=2, relief=tk.RAISED)		
		separator.grid(row=0, column=1, columnspan=5, sticky=tk.W+tk.E, padx=10, pady=1)				


		lbl1=tk.Label(configWindow, text="RFID Reader IP:").grid(row=1, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e1=tk.Entry(configWindow)
		self.e1.grid(row=1, column=1, padx=10, pady=1)
		self.e1.delete(0,tk.END)
		self.e1.insert(0,self.TCP_IP_RFID_READER)
		lbl2=tk.Label(configWindow, text="i.e. 192.168.0.20").grid(row=1, column=2, padx=10, pady=1, sticky=tk.W)				
		
		lbl3=tk.Label(configWindow, text="RFID Reader PORT:").grid(row=2, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e2=tk.Entry(configWindow)
		self.e2.grid(row=2, column=1, padx=10, pady=1)
		self.e2.delete(0,tk.END)
		self.e2.insert(0,self.TCP_PORT_RFID_READER)
		lbl4=tk.Label(configWindow, text="i.e. 2189").grid(row=2, column=2, padx=10, pady=1, sticky=tk.W)				
		
		lbl5=tk.Label(configWindow, text="TCP BUFFER:").grid(row=3, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e3=tk.Entry(configWindow)
		self.e3.grid(row=3, column=1, padx=10, pady=1)
		self.e3.delete(0,tk.END)
		self.e3.insert(0,self.BUFFER_SIZE_RFID_READER)					
		lbl6=tk.Label(configWindow, text="i.e. 512").grid(row=3, column=2, padx=10, pady=1, sticky=tk.W)				

		lbl=tk.Label(configWindow, text="Freq. reading RFID:").grid(row=4, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e50=tk.Entry(configWindow)
		self.e50.grid(row=4, column=1, padx=10, pady=1)
		self.e50.delete(0,tk.END)
		self.e50.insert(0,self.FREQ_READ_RFID)
		lbl=tk.Label(configWindow, text="60 (seconds)").grid(row=4, column=2, padx=10, pady=1, sticky=tk.W)				
		
		lbl=tk.Label(configWindow, text="Freq. accessing platform:").grid(row=1, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e51=tk.Entry(configWindow)
		self.e51.grid(row=1, column=4, padx=10, pady=1)
		self.e51.delete(0,tk.END)
		self.e51.insert(0,self.FREQ_ACCESS_PLATF)		
		lbl=tk.Label(configWindow, text="600 (sec)").grid(row=1, column=5, padx=10, pady=1, sticky=tk.W)				

		lbl=tk.Label(configWindow, text="Truck Id:").grid(row=2, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e52=tk.Entry(configWindow)
		self.e52.grid(row=2, column=4, padx=10, pady=1)
		self.e52.delete(0,tk.END)
		self.e52.insert(0,self.TRUCK_ID)		
		lbl=tk.Label(configWindow, text="001 (num)").grid(row=2, column=5, padx=10, pady=1, sticky=tk.W)				

		lbl=tk.Label(configWindow, text="Comments:").grid(row=3, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e53=tk.Entry(configWindow)
		self.e53.grid(row=3, column=4, padx=10, pady=1)
		self.e53.delete(0,tk.END)
		self.e53.insert(0,self.COMMENTS)		
		lbl=tk.Label(configWindow, text="Any Text").grid(row=3, column=5, padx=10, pady=1, sticky=tk.W)				
		
		
		lbl7=tk.Label(configWindow, text="RFID reader configuration").grid(row=6, column=0, padx=0, pady=1, sticky=tk.E)				

		separator1=tk.Frame(configWindow, height=2, width=100, borderwidth=2, relief=tk.RAISED)		
		separator1.grid(row=6, column=1, columnspan=5, sticky=tk.W+tk.E, padx=10, pady=1)			

		lbl8=tk.Label(configWindow, text="ATTRIB ANTS:").grid(row=7, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e4=tk.Entry(configWindow)
		self.e4.grid(row=7, column=1, padx=10, pady=1)
		self.e4.delete(0,tk.END)
		self.e4.insert(0,self.ATTRIB_ANTS)					
		cfgBtn1=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn1_click)
		cfgBtn1.grid(row=7, column=2, padx=10, pady=1, sticky=tk.W)

		lbl9=tk.Label(configWindow, text="ATTRIB TAGTYPE:").grid(row=7, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e5=tk.Entry(configWindow)
		self.e5.grid(row=7, column=4, padx=10, pady=1)
		self.e5.delete(0,tk.END)
		self.e5.insert(0,self.ATTRIB_TAGTYPE)					
		cfgBtn2=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn2_click)
		cfgBtn2.grid(row=7, column=5, padx=10, pady=1, sticky=tk.W)

		lbl10=tk.Label(configWindow, text="ATTRIB FIELDSTRENGTH:").grid(row=8, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e6=tk.Entry(configWindow)
		self.e6.grid(row=8, column=1, padx=10, pady=1)
		self.e6.delete(0,tk.END)
		self.e6.insert(0,self.ATTRIB_FIELDSTRENGTH)					
		cfgBtn3=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn3_click)
		cfgBtn3.grid(row=8, column=2, padx=10, pady=1, sticky=tk.W)
		
		lbl11=tk.Label(configWindow, text="ATTRIB RDTRIES:").grid(row=8, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e7=tk.Entry(configWindow)
		self.e7.grid(row=8, column=4, padx=10, pady=1)
		self.e7.delete(0,tk.END)
		self.e7.insert(0,self.ATTRIB_RDTRIES)					
		cfgBtn4=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn4_click)
		cfgBtn4.grid(row=8, column=5, padx=10, pady=1, sticky=tk.W)
		
		lbl12=tk.Label(configWindow, text="ATTRIB RPTTIMEOUT:").grid(row=9, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e8=tk.Entry(configWindow)
		self.e8.grid(row=9, column=1, padx=10, pady=1)
		self.e8.delete(0,tk.END)
		self.e8.insert(0,self.ATTRIB_RPTTIMEOUT)					
		cfgBtn5=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn5_click)
		cfgBtn5.grid(row=9, column=2, padx=10, pady=1, sticky=tk.W)
		
		lbl13=tk.Label(configWindow, text="ATTRIB IDTIMEOUT:").grid(row=9, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e9=tk.Entry(configWindow)
		self.e9.grid(row=9, column=4, padx=10, pady=1)
		self.e9.delete(0,tk.END)
		self.e9.insert(0,self.ATTRIB_IDTIMEOUT)					
		cfgBtn6=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn6_click)
		cfgBtn6.grid(row=9, column=5, padx=10, pady=1, sticky=tk.W)

		lbl13=tk.Label(configWindow, text="ATTRIB ANTTIMEOUT:").grid(row=10, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e10=tk.Entry(configWindow)
		self.e10.grid(row=10, column=1, padx=10, pady=1)
		self.e10.delete(0,tk.END)
		self.e10.insert(0,self.ATTRIB_ANTTIMEOUT)					
		cfgBtn7=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn7_click)
		cfgBtn7.grid(row=10, column=2, padx=10, pady=1, sticky=tk.W)
		
		lbl14=tk.Label(configWindow, text="ATTRIB IDTRIES:").grid(row=10, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e11=tk.Entry(configWindow)
		self.e11.grid(row=10, column=4, padx=10, pady=1)
		self.e11.delete(0,tk.END)
		self.e11.insert(0,self.ATTRIB_IDTRIES)					
		cfgBtn8=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn8_click)
		cfgBtn8.grid(row=10, column=5, padx=10, pady=1, sticky=tk.W)

		lbl15=tk.Label(configWindow, text="ATTRIB ANTTRIES:").grid(row=11, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e12=tk.Entry(configWindow)
		self.e12.grid(row=11, column=1, padx=10, pady=1)
		self.e12.delete(0,tk.END)
		self.e12.insert(0,self.ATTRIB_ANTTRIES)					
		cfgBtn9=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn9_click)
		cfgBtn9.grid(row=11, column=2, padx=10, pady=1, sticky=tk.W)
		
		lbl16=tk.Label(configWindow, text="ATTRIB WRTRIES:").grid(row=11, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e13=tk.Entry(configWindow)
		self.e13.grid(row=11, column=4, padx=10, pady=1)
		self.e13.delete(0,tk.END)
		self.e13.insert(0,self.ATTRIB_WRTRIES)					
		cfgBtn10=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn10_click)
		cfgBtn10.grid(row=11, column=5, padx=10, pady=1, sticky=tk.W)

		lbl17=tk.Label(configWindow, text="ATTRIB LOCKTRIES:").grid(row=12, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e14=tk.Entry(configWindow)
		self.e14.grid(row=12, column=1, padx=10, pady=1)
		self.e14.delete(0,tk.END)
		self.e14.insert(0,self.ATTRIB_LOCKTRIES)					
		cfgBtn11=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn11_click)
		cfgBtn11.grid(row=12, column=2, padx=10, pady=1, sticky=tk.W)
		
		lbl18=tk.Label(configWindow, text="ATTRIB SELTRIES:").grid(row=12, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e15=tk.Entry(configWindow)
		self.e15.grid(row=12, column=4, padx=10, pady=1)
		self.e15.delete(0,tk.END)
		self.e15.insert(0,self.ATTRIB_SELTRIES)					
		cfgBtn12=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn12_click)
		cfgBtn12.grid(row=12, column=5, padx=10, pady=1, sticky=tk.W)				
	
		lbl19=tk.Label(configWindow, text="ATTRIB UNSELTRIES:").grid(row=13, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e16=tk.Entry(configWindow)
		self.e16.grid(row=13, column=1, padx=10, pady=1)
		self.e16.delete(0,tk.END)
		self.e16.insert(0,self.ATTRIB_UNSELTRIES)					
		cfgBtn13=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn13_click)
		cfgBtn13.grid(row=13, column=2, padx=10, pady=1, sticky=tk.W)
		
		lbl20=tk.Label(configWindow, text="ATTRIB INITTRIES:").grid(row=13, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e17=tk.Entry(configWindow)
		self.e17.grid(row=13, column=4, padx=10, pady=1)
		self.e17.delete(0,tk.END)
		self.e17.insert(0,self.ATTRIB_INITTRIES)					
		cfgBtn14=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn14_click)
		cfgBtn14.grid(row=13, column=5, padx=10, pady=1, sticky=tk.W)		

		lbl21=tk.Label(configWindow, text="ATTRIB INITIALQ:").grid(row=14, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e18=tk.Entry(configWindow)
		self.e18.grid(row=14, column=1, padx=10, pady=1)
		self.e18.delete(0,tk.END)
		self.e18.insert(0,self.ATTRIB_INITIALQ)					
		cfgBtn15=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn15_click)
		cfgBtn15.grid(row=14, column=2, padx=10, pady=1, sticky=tk.W)
		
		lbl22=tk.Label(configWindow, text="ATTRIB QUERYSEL:").grid(row=14, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e19=tk.Entry(configWindow)
		self.e19.grid(row=14, column=4, padx=10, pady=1)
		self.e19.delete(0,tk.END)
		self.e19.insert(0,self.ATTRIB_QUERYSEL)					
		cfgBtn16=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn16_click)
		cfgBtn16.grid(row=14, column=5, padx=10, pady=1, sticky=tk.W)

		lbl23=tk.Label(configWindow, text="ATTRIB QUERYTARGET:").grid(row=15, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e20=tk.Entry(configWindow)
		self.e20.grid(row=15, column=1, padx=10, pady=1)
		self.e20.delete(0,tk.END)
		self.e20.insert(0,self.ATTRIB_QUERYTARGET)					
		cfgBtn17=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn17_click)
		cfgBtn17.grid(row=15, column=2, padx=10, pady=1, sticky=tk.W)
		
		lbl24=tk.Label(configWindow, text="ATTRIB SESSION:").grid(row=15, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e21=tk.Entry(configWindow)
		self.e21.grid(row=15, column=4, padx=10, pady=1)
		self.e21.delete(0,tk.END)
		self.e21.insert(0,self.ATTRIB_SESSION)					
		cfgBtn18=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn18_click)
		cfgBtn18.grid(row=15, column=5, padx=10, pady=1, sticky=tk.W)

		lbl25=tk.Label(configWindow, text="ATTRIB LBTCHANNEL:").grid(row=16, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e22=tk.Entry(configWindow)
		self.e22.grid(row=16, column=1, padx=10, pady=1)
		self.e22.delete(0,tk.END)
		self.e22.insert(0,self.ATTRIB_LBTCHANNEL)					
		cfgBtn19=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn19_click)
		cfgBtn19.grid(row=16, column=2, padx=10, pady=1, sticky=tk.W)
		
		lbl26=tk.Label(configWindow, text="ATTRIB SCHEDULEOPT:").grid(row=16, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e23=tk.Entry(configWindow)
		self.e23.grid(row=16, column=4, padx=10, pady=1)
		self.e23.delete(0,tk.END)
		self.e23.insert(0,self.ATTRIB_SCHEDULEOPT)					
		cfgBtn20=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn20_click)
		cfgBtn20.grid(row=16, column=5, padx=10, pady=1, sticky=tk.W)
		
		lbl27=tk.Label(configWindow, text="ATTRIB FIELDSEP:").grid(row=17, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e24=tk.Entry(configWindow)
		self.e24.grid(row=17, column=1, padx=10, pady=1)
		self.e24.delete(0,tk.END)
		self.e24.insert(0,self.ATTRIB_FIELDSEP)					
		cfgBtn21=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn21_click)
		cfgBtn21.grid(row=17, column=2, padx=10, pady=1, sticky=tk.W)
		
		lbl28=tk.Label(configWindow, text="ATTRIB BROADCASTSYNC:").grid(row=17, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e25=tk.Entry(configWindow)
		self.e25.grid(row=17, column=4, padx=10, pady=1)
		self.e25.delete(0,tk.END)
		self.e25.insert(0,self.ATTRIB_BROADCASTSYNC)					
		cfgBtn22=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn22_click)
		cfgBtn22.grid(row=17, column=5, padx=10, pady=1, sticky=tk.W)

		lbl29=tk.Label(configWindow, text="ATTRIB UTCTIME:").grid(row=18, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e26=tk.Entry(configWindow)
		self.e26.grid(row=18, column=1, padx=10, pady=1)
		self.e26.delete(0,tk.END)
		self.e26.insert(0,self.ATTRIB_UTCTIME)					
		cfgBtn23=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn23_click)
		cfgBtn23.grid(row=18, column=2, padx=10, pady=1, sticky=tk.W)
		
		lbl30=tk.Label(configWindow, text="ATTRIB TIMEOUTMODE:").grid(row=18, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e27=tk.Entry(configWindow)
		self.e27.grid(row=18, column=4, padx=10, pady=1)
		self.e27.delete(0,tk.END)
		self.e27.insert(0,self.ATTRIB_TIMEOUTMODE)					
		cfgBtn24=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn24_click)
		cfgBtn24.grid(row=18, column=5, padx=10, pady=1, sticky=tk.W)

		lbl31=tk.Label(configWindow, text="ATTRIB NOTAGRPT:").grid(row=19, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e28=tk.Entry(configWindow)
		self.e28.grid(row=19, column=1, padx=10, pady=1)
		self.e28.delete(0,tk.END)
		self.e28.insert(0,self.ATTRIB_NOTAGRPT)					
		cfgBtn25=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn25_click)
		cfgBtn25.grid(row=19, column=2, padx=10, pady=1, sticky=tk.W)
		
		lbl32=tk.Label(configWindow, text="ATTRIB IDREPORT:").grid(row=19, column=3, padx=10, pady=1, sticky=tk.W)				
		self.e29=tk.Entry(configWindow)
		self.e29.grid(row=19, column=4, padx=10, pady=1)
		self.e29.delete(0,tk.END)
		self.e29.insert(0,self.ATTRIB_IDREPORT)					
		cfgBtn26=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn26_click)
		cfgBtn26.grid(row=19, column=5, padx=10, pady=1, sticky=tk.W)
		
		lbl33=tk.Label(configWindow, text="ATTRIB SCHEDOPT:").grid(row=20, column=0, padx=10, pady=1, sticky=tk.W)				
		self.e30=tk.Entry(configWindow)
		self.e30.grid(row=20, column=1, padx=10, pady=1)
		self.e30.delete(0,tk.END)
		self.e30.insert(0,self.ATTRIB_SCHEDOPT)					
		cfgBtn27=tk.Button(configWindow, text='Info', pady=1, command=self.cfgBtn27_click)
		cfgBtn27.grid(row=20, column=2, padx=10, pady=1, sticky=tk.W)
	
		lblExample=tk.Label(configWindow, text="Example:").grid(row=21, column=0, padx=10, pady=1, sticky=tk.W)				
		self.tExample = tk.Text(configWindow, wrap=tk.WORD, height=1)
		self.tExample.grid(row=21, column=1, columnspan=5, padx=10, pady=1, sticky=tk.W+tk.E)
		
		lblDescription=tk.Label(configWindow, text="Description:").grid(row=22, column=0, padx=10, pady=1, sticky=tk.W)				
		self.tDescription = tk.Text(configWindow, wrap=tk.WORD, height=1)
		self.tDescription.grid(row=22, column=1, columnspan=5, padx=10, pady=1, sticky=tk.W+tk.E)

		separator2=tk.Frame(configWindow, height=2, width=100, borderwidth=2, relief=tk.RAISED)		
		separator2.grid(row=23, columnspan=6, sticky=tk.W+tk.E, padx=10, pady=1)	
		
		#bottom Frame
		bottomFrame=tk.Frame(configWindow)
		bottomFrame.grid(row=24, column=0, columnspan=6) 
			
		imageLogoUe=Image.open("img/logo_ue.jpg")
		imageLogoUe=imageLogoUe.resize((58, 35), Image.ANTIALIAS)
		imgLogoUe=ImageTk.PhotoImage(imageLogoUe)		
			
		lblLogoUe=tk.Label(bottomFrame, image=imgLogoUe)
		lblLogoUe.image=imgLogoUe
		lblLogoUe.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

		imageLogoSlope=Image.open("img/logo_slope.png")
		imageLogoSlope=imageLogoSlope.resize((43, 35))
		imgLogoSlope=ImageTk.PhotoImage(imageLogoSlope)		
			
		lblLogoUe=tk.Label(bottomFrame, image=imgLogoSlope)
		lblLogoUe.image=imgLogoSlope
		lblLogoUe.grid(row=0, column=1, padx=10, pady=10)			

		imageSaveXml=Image.open("img/floppy-disk.png")
		imgSaveXml=ImageTk.PhotoImage(imageSaveXml)		
		
		saveXmlButton=tk.Button(bottomFrame, image=imgSaveXml, command=self.saveXmlFile)
		saveXmlButton.image=imgSaveXml
		saveXmlButton.grid(row=0, column=2, padx=10, pady=2)	
				
		imageExit=Image.open("img/exit.png")
		imgExit=ImageTk.PhotoImage(imageExit)
						
		btnExit=tk.Button(bottomFrame, image=imgExit, command=configWindow.destroy)
		btnExit.image=imgExit
		btnExit.grid(row=0, column=3, padx=10, pady=2)		
	
	
	"""sends a single instruction to the RFID Reader"""		
	def btnSendTestCommand_click(self):

		command= self.eTestRfid.get()+'\n'
		self.testLog.insert(tk.END, "sending command: " + command )			
		response = self.sendSingleBriCommand(command)
		newResponse=response.replace('\r','')
		self.testLog.insert(tk.END, newResponse)				
		self.testLog.yview(tk.END)  #to keep the last text always visible
		

	"""sends all configuration  instructions to the reader, and after it reads tags"""	
	def btnLoadTestCommand_click(self):			
	
		#here we create the desired list of commands
		self.commandList =[
		'VER\r\n',
		'PING TIME\r\n',
		'ATTRIB ANTS=' + self.ATTRIB_ANTS + '\r\n', 			
		'ATTRIB TAGTYPE=' + self.ATTRIB_TAGTYPE + '\r\n', 
		'ATTRIB FIELDSTRENGTH=' + self.ATTRIB_FIELDSTRENGTH + '\r\n', 
		'ATTRIB RDTRIES=' + self.ATTRIB_RDTRIES + '\r\n', 		
		'ATTRIB RPTTIMEOUT=' + self.ATTRIB_RPTTIMEOUT + '\r\n', 	
		'ATTRIB IDTIMEOUT=' + self.ATTRIB_IDTIMEOUT + '\r\n', 	
		'ATTRIB ANTTIMEOUT=' + self.ATTRIB_ANTTIMEOUT + '\r\n', 	
		'ATTRIB IDTRIES=' + self.ATTRIB_IDTRIES + '\r\n', 		
		'ATTRIB ANTTRIES=' + self.ATTRIB_ANTTRIES + '\r\n', 		
		'ATTRIB WRTRIES=' + self.ATTRIB_WRTRIES + '\r\n', 		
		'ATTRIB LOCKTRIES='+ self.ATTRIB_LOCKTRIES + '\r\n', 	
		'ATTRIB SELTRIES=' + self.ATTRIB_SELTRIES + '\r\n', 		
		'ATTRIB UNSELTRIES=' + self.ATTRIB_UNSELTRIES + '\r\n', 	
		'ATTRIB INITTRIES=' + self.ATTRIB_INITTRIES + '\r\n', 	
		'ATTRIB INITIALQ=' + self.ATTRIB_INITIALQ + '\r\n', 		
		'ATTRIB QUERYSEL=' + self.ATTRIB_QUERYSEL + '\r\n', 		
		'ATTRIB QUERYTARGET=' + self.ATTRIB_QUERYTARGET + '\r\n', 	
		'ATTRIB SESSION=' + self.ATTRIB_SESSION + '\r\n', 		
		'ATTRIB LBTCHANNEL=' + self.ATTRIB_LBTCHANNEL + '\r\n', 	
		'ATTRIB SCHEDULEOPT=' + self.ATTRIB_SCHEDULEOPT + '\r\n', 	
		'ATTRIB FIELDSEP="' + self.ATTRIB_FIELDSEP + '"\r\n', 	
		'ATTRIB BROADCASTSYNC=' + self.ATTRIB_BROADCASTSYNC + '\r\n', 
		'ATTRIB UTCTIME=' + self.ATTRIB_UTCTIME + '\r\n', 	
		'ATTRIB TIMEOUTMODE=' + self.ATTRIB_TIMEOUTMODE + '\r\n', 
		'ATTRIB NOTAGRPT=' + self.ATTRIB_NOTAGRPT + '\r\n', 	
		'ATTRIB IDREPORT=' + self.ATTRIB_IDREPORT+ '\r\n', 	
		'ATTRIB SCHEDOPT=' + self.ATTRIB_SCHEDOPT + '\r\n'] 		
		
		# update of the number of Commands
		self.numCommands=[len(self.commandList), 0]
				
		self.sendMultipleBriCommands()
		

	"""sends a read tag instruction to the RFID reader"""	
	def btnReadTestCommand_click(self):
		command= 'Read RSSI ANT\r\n'
		self.testLog.insert(tk.END, "sending command: " + command )			
		response = self.sendSingleBriCommand(command)
		#self.testLog.insert(tk.END, 'Response:\n'+ repr(response) + '\n')			
		newResponse=response.replace('\r','')
		self.testLog.insert(tk.END, newResponse)
		if newResponse.count('NOTAG') == 1:
			numberTags = 0
		else:
			numberTags=newResponse.count('\n') -1 #to remove the ok line
		self.testLog.insert(tk.END, "number of tags: " + str(numberTags) + "\n")				
		self.testLog.yview(tk.END)  #to keep the last text always visible


	"""sends a write tag instructino to the RFID reader"""	
	def btnWriteTestCommand_click(self):

		command= 'W EPCID =' + self.eTagData.get()+'\r\n'
		self.testLog.insert(tk.END, "sending command: " + command )			
		response = self.sendSingleBriCommand(command)
		
		newResponse=response.replace('\r','')
		self.testLog.insert(tk.END, newResponse)				
		self.testLog.yview(tk.END)  #to keep the last text always visible

	
	"""sends a read tag instruction to the RFID reader"""	
	def btnResetTestCommand_click(self):
		command= 'Reset\r\n'
		self.testLog.insert(tk.END, "sending command: " + command )			
		response = self.sendSingleBriCommand(command)
		self.testLog.insert(tk.END, 'Response:\n'+ repr(response) + '\n')			
		newResponse=response.replace('\r','')
		self.testLog.insert(tk.END, newResponse)				
		self.testLog.yview(tk.END)  #to keep the last text always visible

	
	"""read all tags trough the Reader and instroduces the info in the database"""		
	def btnStoreInDb_click(self):

		command= 'Read\r\n'
		self.testLog.insert(tk.END, "sending command: " + command )			
		response = self.sendSingleBriCommand(command)
		
		self.testLog.insert(tk.END, 'Response received:\n'+ repr(response) + '\n')				
		
		response=response[:-5]   #Here we eliminate ending 5(O) 4(K) 3(>) 2(\r) 1(\n)	)
				
		listResponses=response.split('\r\n') 	# this leaves an empty element in the list
			
		listPoints=[]
		
		#for the number of responses in the list, do...
		for i in range(len(listResponses)):
			#we create a point
			p = databaseEntry()
			
			#we put the value in place
			p.EPCData=listResponses.pop()
			
			
			if p.EPCData != ('NOTAG') and p.EPCData != ('')and self.isThereGps:
				
				p.latitude = self.myLastGpsPoint.Latitude
				p.longitude=self.myLastGpsPoint.Longitude
				p.altitude=self.myLastGpsPoint.Altitude
				p.time=self.myLastGpsPoint.Time
				p.speed=self.myLastGpsPoint.Speed
				p.truckId=self.TRUCK_ID
				p.comments=self.COMMENTS
				
				self.testLog.insert(tk.END, 'time ' + p.time + ' . \n')	
																						
				#we add it to the list	of points
				listPoints.append(p)				
				self.testLog.insert(tk.END, 'point generated\n')
			else:
				self.testLog.insert(tk.END, 'no tag has beed detected or stored.\n')
		
		# For the number of points in the list, do:
		for i in range(len(listPoints)):
			p=listPoints.pop()
						
			self.storePointInDb(p)			
			self.testLog.insert(tk.END, 'point ' + p.EPCData + ' stored. \n')

		self.testLog.yview(tk.END)


	"""connect to SLOPE and tell result"""	
	def btnTestGprs_click(self):
		#url='http://www.google.com'
		url='https://slopefis.mhgsystems.com/slope-fis/rest/customers/'
		headers ={'Accept':'application/json'}		

		self.testLog.insert(tk.END, "Connecting to " + url + "\n")	
			
		try:
			r=requests.get(url, headers=headers, auth=('test','test'), verify=False)
		
			self.testLog.insert(tk.END, "Received: " +r.text + "\n")
			self.testLog.insert(tk.END, "Status Code: " +str(r.status_code) + "\n")		
		
			if r.status_code ==200:	 
				self.testLog.insert(tk.END, "GPRS works correctly\n")						
			else:
				self.testLog.insert(tk.END, "GPRS does not work correctly\n")	

		except:
			self.testLog.insert(tk.END, "exception happened when acceding. \n")
	


	"""checks last received gps point and shows it in the testLog"""
	def btnReadGpsData_click(self):

		self.testLog.insert(tk.END, 'Last Measured point: Time ' + str(self.myLastGpsPoint.Time) + '\n')
		self.testLog.insert(tk.END, 'Last Measured point: Altitude ' + str(self.myLastGpsPoint.Altitude) + '\n')
		self.testLog.yview(tk.END)  #to keep the last text always visible
		
	"""connects to the database and executes query to introduce points"""
	def storePointInDb(self, p):

		# first we try to connect
		try:
			conn=psycopg2.connect("dbname='slope_db' user='postgres' host='localhost' password='p@ssw0rd'")
			#self.testLog.insert(tk.END, 'database connected!!\n')
		except:
			self.testLog.insert(tk.END, 'Exception: unable to connect to the database\n') 
			conn.close()
	
		#then we create a cursor to connect
		cur=conn.cursor()
		
		#now we execute a query
		query="INSERT INTO itruck (truck_id, time_created, longitude, latitude, altitude, speed, epc_data, is_sent, comments) VALUES (" + str(p.truckId) + ", '" + str(p.time)+ "', " + str(p.longitude) + ", " + str(p.latitude) + ", " + str(p.altitude) + ", " + str(p.speed) + ", '" + p.EPCData + "', " + str(p.isSent) + ", '" + p.comments + "')"
		
		#self.testLog.insert(tk.END, query)
		
		cur.execute(query)

		#make changes persistent
		conn.commit()
		
		# and here we close the db connection
		cur.close()
		conn.close()


	"""sends multiple Bri commands to the RFID reader, with some time separation"""
	def sendMultipleBriCommands(self):
	
		
		if (self.numCommands[0] > 0) and (self.numCommands[0] > self.numCommands[1]):
			self.testLog.insert(tk.END, self.commandList[self.numCommands[1]])
			response = self.sendSingleBriCommand(self.commandList[self.numCommands[1]])
			newResponse=response.replace('\r','')
			self.testLog.insert(tk.END, newResponse)
			self.testLog.yview(tk.END)
			
			self.numCommands[1] = self.numCommands[1]+1
			
			self.root.after(10, self.sendMultipleBriCommands) #tkinter execute this method afer 10 ms
		
		else:
			self.numCommands=[0, 0]
			self.commandList=['']


	"""creates a TCP socket, sends a single command to the reader, and receive the answer"""
	def sendSingleBriCommand(self, command):
	
		 
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#self.testLog.insert(tk.END,'socket created\n')   
			s.connect((self.TCP_IP_RFID_READER, self.TCP_PORT_RFID_READER))
			#self.testLog.insert(tk.END,'socket connected\n')   		
			s.send(command.encode('utf-8'))
			#self.testLog.insert(tk.END,'message sent succesfuly\n') 
			#some time is needed to receive all information from the RFID reader and fill the buffer
			time.sleep(0.5) 
			responseAsByte=s.recv(self.BUFFER_SIZE_RFID_READER)
			#self.testLog.insert(tk.END,'message received succesffuly\n') 
			s.close()  
			responseAsString=responseAsByte.decode('utf-8')
		
		except:
			s.close()	
			Worker2.notFound()
			responseAsString= "exception when doing "+ command
		
		finally:
			return responseAsString

			
	"""takes all info in the configuration widgets and generate a new xml config file"""			
	def saveXmlFile(self):
		
		config=ET.Element("config")
		
		MainConfig=ET.SubElement(config, "MainConfig")	
		
		ET_TCP_IP_RFID_READER=ET.SubElement(MainConfig, "TCP_IP_RFID_READER")	
		ET_TCP_IP_RFID_READER.text=(self.e1.get())
		self.TCP_IP_RFID_READER=(self.e1.get())
	
		ET_TCP_PORT_RFID_READER=ET.SubElement(MainConfig, "TCP_PORT_RFID_READER")	
		ET_TCP_PORT_RFID_READER.text=(self.e2.get())
		self.TCP_PORT_RFID_READER=int((self.e2.get()))
				
		ET_BUFFER_SIZE_RFID_READER=ET.SubElement(MainConfig, "BUFFER_SIZE_RFID_READER")	
		ET_BUFFER_SIZE_RFID_READER.text=(self.e3.get())	
		self.BUFFER_SIZE_RFID_READER=int((self.e3.get()))	
		
		FREQ_READ_RFID=ET.SubElement(MainConfig, "FREQ_READ_RFID")	
		FREQ_READ_RFID.text=(self.e50.get())	
		self.FREQ_READ_RFID=int((self.e50.get()))	
			
		FREQ_ACCESS_PLATF=ET.SubElement(MainConfig, "FREQ_ACCESS_PLATF")	
		FREQ_ACCESS_PLATF.text=(self.e51.get())	
		self.FREQ_ACCESS_PLATF=int((self.e51.get()))
		
		TRUCK_ID=ET.SubElement(MainConfig, "TRUCK_ID")	
		TRUCK_ID.text=(self.e52.get())	
		self.TRUCK_ID=int((self.e52.get()))	
			
		COMMENTS=ET.SubElement(MainConfig, "COMMENTS")	
		COMMENTS.text=(self.e53.get())	
		self.COMMENTS=(self.e53.get())		
		
		RfidReaderConfig=ET.SubElement(config, "RfidReaderConfig")	
		
		ET_ATTRIB_ANTS=ET.SubElement(RfidReaderConfig, "ATTRIB_ANTS")	
		ET_ATTRIB_ANTS.text=(self.e4.get())
		self.ATTRIB_ANTS=(self.e4.get())
	
		ET_ATTRIB_TAGTYPE=ET.SubElement(RfidReaderConfig, "ATTRIB_TAGTYPE")	
		ET_ATTRIB_TAGTYPE.text=(self.e5.get())
		self.ATTRIB_TAGTYPE=(self.e5.get())
				
		ET_ATTRIB_FIELDSTRENGTH=ET.SubElement(RfidReaderConfig, "ATTRIB_FIELDSTRENGTH")	
		ET_ATTRIB_FIELDSTRENGTH.text=(self.e6.get())	
		self.ATTRIB_FIELDSTRENGTH=(self.e6.get())		
		
		ET_ATTRIB_RDTRIES=ET.SubElement(RfidReaderConfig, "ATTRIB_RDTRIES")	
		ET_ATTRIB_RDTRIES.text=(self.e7.get())
		self.ATTRIB_RDTRIES=(self.e7.get())
	
		ET_ATTRIB_RPTTIMEOUT=ET.SubElement(RfidReaderConfig, "ATTRIB_RPTTIMEOUT")	
		ET_ATTRIB_RPTTIMEOUT.text=(self.e8.get())
		self.ATTRIB_RPTTIMEOUT=(self.e8.get())
				
		ET_ATTRIB_IDTIMEOUT=ET.SubElement(RfidReaderConfig, "ATTRIB_IDTIMEOUT")	
		ET_ATTRIB_IDTIMEOUT.text=(self.e9.get())	
		self.ATTRIB_IDTIMEOUT=(self.e9.get())	

		ET_ATTRIB_ANTTIMEOUT=ET.SubElement(RfidReaderConfig, "ATTRIB_ANTTIMEOUT")	
		ET_ATTRIB_ANTTIMEOUT.text=(self.e10.get())	
		self.ATTRIB_ANTTIMEOUT=(self.e10.get())	
		
		ET_ATTRIB_IDTRIES=ET.SubElement(RfidReaderConfig, "ATTRIB_IDTRIES")	
		ET_ATTRIB_IDTRIES.text=(self.e11.get())	
		self.ATTRIB_IDTRIES=(self.e11.get())	
		
		ET_ATTRIB_ANTTRIES=ET.SubElement(RfidReaderConfig, "ATTRIB_ANTTRIES")	
		ET_ATTRIB_ANTTRIES.text=(self.e12.get())	
		self.ATTRIB_ANTTRIES=(self.e12.get())
		
		ET_ATTRIB_WRTRIES=ET.SubElement(RfidReaderConfig, "ATTRIB_WRTRIES")	
		ET_ATTRIB_WRTRIES.text=(self.e13.get())	
		self.ATTRIB_WRTRIES=(self.e13.get())
		
		ET_ATTRIB_LOCKTRIES=ET.SubElement(RfidReaderConfig, "ATTRIB_LOCKTRIES")	
		ET_ATTRIB_LOCKTRIES.text=(self.e14.get())	
		self.ATTRIB_LOCKTRIES=(self.e14.get())
		
		ET_ATTRIB_SELTRIES=ET.SubElement(RfidReaderConfig, "ATTRIB_SELTRIES")	
		ET_ATTRIB_SELTRIES.text=(self.e15.get())	
		self.ATTRIB_SELTRIES=(self.e15.get())
		
		ET_ATTRIB_UNSELTRIES=ET.SubElement(RfidReaderConfig, "ATTRIB_UNSELTRIES")	
		ET_ATTRIB_UNSELTRIES.text=(self.e16.get())	
		self.ATTRIB_UNSELTRIES=(self.e16.get())

		ET_ATTRIB_INITTRIES=ET.SubElement(RfidReaderConfig, "ATTRIB_INITTRIES")	
		ET_ATTRIB_INITTRIES.text=(self.e17.get())	
		self.ATTRIB_INITTRIES=(self.e17.get())
		
		ET_ATTRIB_INITIALQ=ET.SubElement(RfidReaderConfig, "ATTRIB_INITIALQ")	
		ET_ATTRIB_INITIALQ.text=(self.e18.get())	
		self.ATTRIB_INITIALQ=(self.e18.get())
		
		ET_ATTRIB_QUERYSEL=ET.SubElement(RfidReaderConfig, "ATTRIB_QUERYSEL")	
		ET_ATTRIB_QUERYSEL.text=(self.e19.get())	
		self.ATTRIB_QUERYSEL=(self.e19.get())

		ET_ATTRIB_QUERYTARGET=ET.SubElement(RfidReaderConfig, "ATTRIB_QUERYTARGET")	
		ET_ATTRIB_QUERYTARGET.text=(self.e20.get())	
		self.ATTRIB_QUERYTARGET=(self.e20.get())
		
		ET_ATTRIB_SESSION=ET.SubElement(RfidReaderConfig, "ATTRIB_SESSION")	
		ET_ATTRIB_SESSION.text=(self.e21.get())	
		self.ATTRIB_SESSION=(self.e21.get())
		
		ET_ATTRIB_LBTCHANNEL=ET.SubElement(RfidReaderConfig, "ATTRIB_LBTCHANNEL")	
		ET_ATTRIB_LBTCHANNEL.text=(self.e22.get())	
		self.ATTRIB_LBTCHANNEL=(self.e22.get())

		ET_ATTRIB_SCHEDULEOPT=ET.SubElement(RfidReaderConfig, "ATTRIB_SCHEDULEOPT")	
		ET_ATTRIB_SCHEDULEOPT.text=(self.e23.get())	
		self.ATTRIB_SCHEDULEOPT=(self.e23.get())
		
		ET_ATTRIB_FIELDSEP=ET.SubElement(RfidReaderConfig, "ATTRIB_FIELDSEP")	
		ET_ATTRIB_FIELDSEP.text=(self.e24.get())	
		self.ATTRIB_FIELDSEP=(self.e24.get())
		
		ET_ATTRIB_BROADCASTSYNC=ET.SubElement(RfidReaderConfig, "ATTRIB_BROADCASTSYNC")	
		ET_ATTRIB_BROADCASTSYNC.text=(self.e25.get())	
		self.ATTRIB_BROADCASTSYNC=(self.e25.get())

		ET_ATTRIB_UTCTIME=ET.SubElement(RfidReaderConfig, "ATTRIB_UTCTIME")	
		ET_ATTRIB_UTCTIME.text=(self.e26.get())	
		self.ATTRIB_UTCTIME=(self.e26.get())
		
		ET_ATTRIB_TIMEOUTMODE=ET.SubElement(RfidReaderConfig, "ATTRIB_TIMEOUTMODE")	
		ET_ATTRIB_TIMEOUTMODE.text=(self.e27.get())	
		self.ATTRIB_TIMEOUTMODE=(self.e27.get())
		
		ET_ATTRIB_NOTAGRPT=ET.SubElement(RfidReaderConfig, "ATTRIB_NOTAGRPT")	
		ET_ATTRIB_NOTAGRPT.text=(self.e28.get())	
		self.ATTRIB_NOTAGRPT=(self.e28.get())		

		ET_ATTRIB_IDREPORT=ET.SubElement(RfidReaderConfig, "ATTRIB_IDREPORT")	
		ET_ATTRIB_IDREPORT.text=(self.e29.get())	
		self.ATTRIB_IDREPORT=(self.e29.get())
		
		ET_ATTRIB_SCHEDOPT=ET.SubElement(RfidReaderConfig, "ATTRIB_SCHEDOPT")	
		ET_ATTRIB_SCHEDOPT.text=(self.e30.get())	
		self.ATTRIB_SCHEDOPT=(self.e30.get())
			
		tree =ET.ElementTree(config)
		tree.write("config.xml")
		
		self.mainLog.insert(tk.END, "Xml file generated succcessfully\n")
		self.mainLog.yview(tk.END)  #to keep the last text always visible
		
		#then we update the Rfid worker values
		Worker2.updateValues(self.myRfidQueue, self.isTruckOn, self.FREQ_READ_RFID, self.TCP_IP_RFID_READER, self.TCP_PORT_RFID_READER, self.BUFFER_SIZE_RFID_READER)


	""" destroys the main application window"""			
	def exitBtn_click(self):

		self.root.destroy()


	"""takes all the text existing in the testLog and saves it in a text File"""
	def saveLogButton_click(self):
	
	
		currentDate = str(datetime.datetime.now().strftime('%x').replace("/", "-"))
		currentTime=str(datetime.datetime.now().strftime('%X').replace(":", "-"))
		fileName=currentDate + '_' + currentTime + '_Log.txt'
		try:
			#self.testLog.insert(tk.END, fileName + "\n")
			f=open(fileName, 'w')
			#self.testLog.insert(tk.END, "file object opened\n")
			f.write(self.mainLog.get (1.0, tk.END))
			#self.testLog.insert(tk.END, "file written\n")
			f.close()
			#self.testLog.insert(tk.END, "file object closed\n")
			self.mainLog.insert(tk.END, "Log File created: " + fileName + "\n")
		except: 
			self.mainLog.insert(tk.END, "Exception when writting a file\n")	


	def cfgBtn1_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 1,2,3,4")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Defines de sequence of antennas when reading")
		self.e4.focus()

	def cfgBtn2_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. EPCC1G2")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Defines the tag to be read")	
		self.e5.focus()
		
	def cfgBtn3_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 29DB,29DB,29DB,29DB")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Define the RF power for each antenna")
		self.e6.focus()

	def cfgBtn4_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 3")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Number of attempts to read a tag before a response is returned")
		self.e7.focus()

	def cfgBtn5_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 0")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Sets delay in response")
		self.e8.focus()
		
	def cfgBtn6_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 4000")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Sets maximum time attempting to read tags")
		self.e9.focus()

	def cfgBtn7_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 0")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Sets maximum time attempting to use antenna when reading tags")
		self.e10.focus()

	def cfgBtn8_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 1")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Sets number of times an attemp is made to read tags")
		self.e11.focus()

	def cfgBtn9_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 1")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Sets number of times each antenna is used  for Read/Write")
		self.e12.focus()

	def cfgBtn10_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 3")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Sets number of times an attempt is made to Write Data")
		self.e13.focus()

	def cfgBtn11_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 3")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Sets number of times the lock algorithm is executed before answering")
		self.e14.focus()

	def cfgBtn12_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 1")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Sets number of times a group select is attempted")
		self.e15.focus()

	def cfgBtn13_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 1")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Sets number of times a group unselect is attempted")
		self.e16.focus()

	def cfgBtn14_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 1")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Sets initialization tries")
		self.e17.focus()

	def cfgBtn15_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 1")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Definite Q parameter value of the query command")
		self.e18.focus()

	def cfgBtn16_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 4")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Define sel field for query commands")
		self.e19.focus()
	
	def cfgBtn17_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. A")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Define target field for query commands")
		self.e20.focus()

	def cfgBtn18_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 1")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Define session parameter")		
		self.e21.focus()
			
	def cfgBtn19_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 7")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Define channel for Listen-Before-Talk algorithm")
		self.e22.focus()

	def cfgBtn20_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 1")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Define how antennas are switched")
		self.e23.focus()
			
	def cfgBtn21_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. ' '")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Define separator in output")
		self.e24.focus()

	def cfgBtn22_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 0")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Value of UTCTime sent in BroadcastsSync commands")
		self.e25.focus()

	def cfgBtn23_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 1094")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Define the usage of timeout and tries attributes")
		self.e26.focus()

	def cfgBtn24_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. OFF")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Define separator in output")
		self.e27.focus()
	
	def cfgBtn25_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. ON")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Send a message when no tags are found")
		self.e28.focus()

	def cfgBtn26_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. ON")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Configure reader to send tag identifiers when a command is executed")
		self.e29.focus()

	def cfgBtn27_click(self):
		self.tExample.delete("1.0", tk.END)
		self.tExample.insert(tk.END, "i.e. 1")
		self.tDescription.delete("1.0", tk.END)
		self.tDescription.insert(tk.END, "Same as SCHEDULEOPT")
		self.e30.focus()

	
		
"""	class to create the Gps-measuring thread"""	
class gpsWorkerThread(threading.Thread):
	
	
	def __init__(self, receivedQueue):	
		"""Constructor and setting variables"""	
	
		self.isRunning = True
		self.myGpsQueue = receivedQueue
		self.myPoint= gpsPoint()
		
		threading.Thread.__init__(self)	#necessary or we will have an error
		
	
	def run(self):
		"""
		Main method
		"""
		
		print('GPS worker is alive and kicking'.encode('utf-8').decode('utf-8'))	
		# This creates a socket to connect to the GPS serial device
		the_connection=gps3.GPSDSocket()
		
		# This created an adapter to recover and translate data from the socket 
		the_fix=gps3.Fix()
					
		# It is very imporant to stop the thread from time to time
		# To allow execution of the main tkinter window		
		
			
		try:				
			for new_data in the_connection: #always inside here because of big amount of data									
				
				if new_data:
					the_fix.refresh(new_data) 
						
				if not isinstance(the_fix.TPV['speed'],str):
					self.myPoint.Speed = the_fix.TPV['speed']
					self.myPoint.Latitude=the_fix.TPV['lat']
					self.myPoint.Longitude=the_fix.TPV['lon']
					self.myPoint.Altitude=the_fix.TPV['alt']
					self.myPoint.Time=the_fix.TPV['time']
									
					self.myGpsQueue.put(self.myPoint)
					
					if isinstance(the_fix.TPV['track'], str):  # 'track' frequently is missing and returns as 'n/a'
						heading = the_fix.TPV['track']
					else:
						heading = round(the_fix.TPV['track'])  # and heading percision in hundreths is just clutter.
				else:
					pass
				
				time.sleep(1)	
				
				if not self.isRunning:
					break				
		
		except:
			pass
			

						
		
	def stop(self):
		print('GPS worker has been erradicated'.encode('utf-8').decode('utf-8'))
		self.isRunning = False
	
	
		
"""	class to create the RFID-measuring thread"""	
class rfidWorkerThread(threading.Thread):
	
	def __init__(self, receivedQueue, isThereReader, isTruckOn, spanBetweenMeasurements, IP, PORT, BUFFER):	
		"""Constructor and setting variables"""	
	
		self.isRunning = True
		self.isTruckOn = isTruckOn #we receive command to read
		self.myRfidQueue = receivedQueue #place to introduce the readed info
		self.spanBetweenMeasurements = spanBetweenMeasurements
	
		self.isThereReader = isThereReader #we receive command to read
		
		self.TCP_IP=IP
		self.TCP_PORT=PORT
		self.BUFFER_SIZE=BUFFER	
		
		self.dateNow=datetime.datetime.now()
		self.dateNext=datetime.datetime.now()
		
		threading.Thread.__init__(self)	#necessary or we will have an error
		
	
	"""Main method"""
	def run(self):
			
		print('RFID worker is alive and kicking'.encode('utf-8').decode('utf-8'))
		
		#this executes always until we change the state with the stop method
		while self.isRunning:
			
			
			#if there is no reader, we try to find one
			if self.isThereReader is False:
						
				command='ping\r\n'
				
				#We do a ping to the reader at the expected IP			
				try:
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
					s.connect((self.TCP_IP, self.TCP_PORT)) 		
					s.send(command.encode('utf-8'))
					#some time is needed to receive all information from the RFID reader and fill the buffer
					time.sleep(0.5) 
					responseAsByte=s.recv(self.BUFFER_SIZE)
					s.close()  
					responseAsString=responseAsByte.decode('utf-8')
				
				except:
					s.close()	
					responseAsString= "exception when doing "+ command
						
				newResponse=responseAsString[0:2] #Here we remove all answered text except from where OK is placed
					
				if newResponse =="OK":	 #to change from byte to utf-8		
					self.isThereReader = True
				else:
					self.isThereReader = False				
			
			
			#only if we are in reading mode...
			if self.isTruckOn is True and self.isThereReader is True:
			
				# We update the date
				self.dateNow=datetime.datetime.now()
			
				# we only read the RFID reader if it is the right time
				if (self.dateNow > self.dateNext):

					command= 'Read\r\n'	
					responseAsString=''
				
					try:
						s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		 
						s.connect((self.TCP_IP, self.TCP_PORT))
				
						s.send(command.encode('utf-8'))

						#some time is needed to receive all information from the RFID reader and fill the buffer
						time.sleep(0.6) 
						
						responseAsByte=s.recv(self.BUFFER_SIZE)

						s.close()  
						responseAsString=responseAsByte.decode('utf-8')
			
					except:
						s.close()	
						self.isThereReader=False
						responseAsString= "exception when doing "+ command
					
					responseAsString=responseAsString[:-5]  # Here we eliminate ending 5(O) 4(K) 3(>) 2(\r) 1(\n)
				
					listResponses=responseAsString.split('\r\n') 	# This leaves an empty element in the list
				
					numberOfTags=0
					#for the number of responses in the list, do...
					for i in range(len(listResponses)):
						
						EPCData=listResponses.pop()			
						
						# We assign the rest of the point data
						if EPCData != ('NOTAG') and EPCData != (''):
							self.myRfidQueue.put(EPCData)
							numberOfTags = numberOfTags+1
							
					#print((str(numberOfTags)+' has been introduced in the Queue').encode('utf-8').decode('utf-8'))					

				
					#update time for next measurement
					self.dateNext = self.dateNow + datetime.timedelta(0, self.spanBetweenMeasurements)
								
			time.sleep(2)	
			
	"""To provide a way for the main method to finish"""
	def stop(self):
		print('RFID worker has died'.encode('utf-8').decode('utf-8'))
		self.isRunning = False		
		
		
	"""To provide a way for the main method to finish"""
	def notFound(self):	
		self.isThereReader = False
		
		
		
	"""To update the values when desired"""
	def updateValues(self, receivedQueue, isTruckOn, spanBetweenMeasurements, IP, PORT, BUFFER):

		self.isTruckOn = isTruckOn #we receive command to read
		self.myRfidQueue = receivedQueue #place to introduce the readed info
		self.TCP_IP=IP
		self.TCP_PORT=PORT
		self.BUFFER_SIZE=BUFFER	
		
		# If we had a change in the span value, we want to use the new value inmediately
		if self.spanBetweenMeasurements is not spanBetweenMeasurements:
			self.spanBetweenMeasurements = spanBetweenMeasurements
			self.dateNow=datetime.datetime.now()
			self.dateNext = self.dateNow + datetime.timedelta(0, self.spanBetweenMeasurements)

	
	
"""	class to create the Gprs thread"""	
class gprsWorkerThread(threading.Thread):
	
	
	def __init__(self, isThereGprs):	
		"""Constructor and setting variables"""	
	
		self.isRunning = True
		self.isThereGprs = isThereGprs
		
		self.url='https://slopefis.mhgsystems.com/slope-fis/rest/customers/'
		self.headers ={'Accept':'application/json'}
		
		threading.Thread.__init__(self)	#necessary or we will have an error
		
	
	def run(self):
		"""
		Main method
		"""
		
		print('GPRS worker is born into the world'.encode('utf-8').decode('utf-8'))	
		
		#this executes always until we change the state with the stop method
		while self.isRunning:
			
			
			#if there is no connection, we try to find one
			if self.isThereGprs is False:									

				#print('trying to access SLOPE portal'.encode('utf-8').decode('utf-8'))
				
				try:
					r=requests.get(self.url, headers=self.headers, auth=('test','test'), verify=False)
					if r.status_code ==200:	 
						self.isThereGprs = True
						print(str(r.status_code).encode('utf-8').decode('utf-8'))
					
					else:
						self.isThereGprs = False	
						print(str(r.status_code).encode('utf-8').decode('utf-8'))	

				except:
					#print('exception happened when acceding \n'.encode('utf-8').decode('utf-8'))
					self.isThereGprs = False	

			time.sleep(5)	
			
	"""To provide a way for the main method to finish"""
	def stop(self):
		print('GPRS worker has died'.encode('utf-8').decode('utf-8'))
		self.isRunning = False		
			
	
			
	
"""		Main loop.
if __name__  works ok in a direct execution. However, if the file is executed from another module, it is not executed
that allows the other module to use de defined functions in this file without problems
"""	
if __name__== '__main__':

	
	# This creates a toplevel widget of Tk, usually the main application window
	mainWindow=tk.Tk()
	
	#this fills the toplevel window
	client = Gui(mainWindow)
	
	#now we create Worker. They report to a queue in mainWindow	
	Worker1=gpsWorkerThread(client.myGpsQueue)
	Worker1.start()
	
	#now we create Worker. They report to a queue in mainWindow	
	Worker2=rfidWorkerThread(client.myRfidQueue, client.isThereRfidReader, client.isTruckOn, client.FREQ_READ_RFID, client.TCP_IP_RFID_READER, client.TCP_PORT_RFID_READER, client.BUFFER_SIZE_RFID_READER)
	Worker2.start()	
	
	Worker3=gprsWorkerThread(client.isThereGprs)
	Worker3.start()
	
	# finally this launches the top level window. Execution line stops here	
	mainWindow.mainloop() 
	
	print('main Window closed'.encode('utf-8').decode('utf-8'))
	#once the mainWindow in closed, this is executed
	Worker1.stop()
	Worker2.stop()
	Worker3.stop()
		
	Worker1.join()
	Worker2.join()	
	Worker3.join()
