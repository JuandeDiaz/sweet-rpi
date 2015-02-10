# started on 04 feb 2015
# SLOPE project
# Task 3.5 
# aim: read RFID and GPS, store it in DB and transmit it via GPRS
# NOTE: app created as a class. This way you do not need global variables, nor to pass arguments 
# NOTE: self is used to make the variable global inside the class
# NOTE: if we do not use self, variables are ceated locally and cannot be shared between methods

# imports
import tkinter as tk
import xml.etree.ElementTree as ET
import socket

class myTkinterApp():
	
	TCP_IP_RFID_READER='192.168.0.68'
	TCP_PORT_RFID_READER=2189
	BUFFER_SIZE_RFID_READER=1024
	
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
	
	
	statusDeLeds='red'

	def __init__(self):

		
		#main window
		self.root= tk.Tk()	 
		self.root.wm_title('iTruck')	#title of the main window 
		
		#Left frame and its contents
		leftFrame=tk.Frame(self.root)
		leftFrame.grid(row=0, column=0, padx=10, pady=2)
		
		#indicators Frame
		indicatorsFrame=tk.Frame(leftFrame)
		indicatorsFrame.grid(row=0, column=0) 
		
		lbl1=tk.Label(indicatorsFrame, text="RFID reader:").grid(row=0, column=0, padx=10, pady=2, sticky=tk.W)		
		self.circleCanvasRFID=tk.Canvas(indicatorsFrame, width=20, height=20)
		self.circleCanvasRFID.grid(row=0, column=1, padx=20, pady=2)
					
		lbl2=tk.Label(indicatorsFrame, text="GPS connection:").grid(row=1, column=0, padx=10, pady=2, sticky=tk.W)		
		self.circleCanvasGPS=tk.Canvas(indicatorsFrame, width=20, height=20)
		self.circleCanvasGPS.grid(row=1, column=1, padx=20, pady=2)	
			
		lbl3=tk.Label(indicatorsFrame, text="GPRS connection:").grid(row=2, column=0, padx=10, pady=2, sticky=tk.W)
		self.circleCanvasGPRS=tk.Canvas(indicatorsFrame, width=20, height=20)
		self.circleCanvasGPRS.grid(row=2, column=1, padx=20, pady=2)
		
		#separator
		sep1=tk.Frame(leftFrame, height=2, width=100, borderwidth=2, relief=tk.RAISED)		
		sep1.grid(row=1, sticky=tk.W+tk.E, padx=10, pady=4)
						
		#testFrame
		testFrame=tk.Frame(leftFrame)
		testFrame.grid(row=2, column=0) 
		
		lbl5=tk.Label(testFrame, text="Testing RFID reader").grid(row=0, column=0, padx=10, pady=2, sticky=tk.W)
		
		lbl6=tk.Label(testFrame, text="Enter BRI Command:").grid(row=1, column=0, padx=10, pady=2, sticky=tk.W)				
		self.eTestRfid=tk.Entry(testFrame)
		self.eTestRfid.grid(row=1, column=1, padx=10, pady=2)				
		btnSend=tk.Button(testFrame, text='Send', command=self.sendTestCommand)
		btnSend.grid(row=1, column=2, padx=10, pady=2)		

		lbl7=tk.Label(testFrame, text="Read tags with current configuration").grid(row=2, column=0, columnspan=2, padx=10, pady=2, sticky=tk.W)							
		btnRead=tk.Button(testFrame, text='Read', command=self.sendReadCommand)
		btnRead.grid(row=2, column=2, padx=10, pady=2)	

		#separator
		sep2=tk.Frame(leftFrame, height=2, width=100, borderwidth=2, relief=tk.RAISED)		
		sep2.grid(row=3, sticky=tk.W+tk.E, padx=10, pady=4)
		
		#controlFrame
		controlsFrame=tk.Frame(leftFrame)
		controlsFrame.grid(row=4, column=0) 
				
		cfgButton=tk.Button(controlsFrame, text='Configure', width=10, command=self.createConfigureWindow)
		cfgButton.grid(row=1, column=0, padx=10, pady=2)
		
		exitBtn=tk.Button(controlsFrame, text='Exit', width=10, command=self.terminate)
		exitBtn.grid(row=1, column=1, padx=10, pady=2)
		
		# Right Frame and its contents
		rightFrame=tk.Frame(self.root, width=200, height=600)
		rightFrame.grid(row=0, column=1, padx=10, pady=2)
		
		statusFrame=tk.Frame(rightFrame, width=200, height=200)
		statusFrame.grid(row=0, column=0, padx=10, pady=2)
		
		scrollbar=tk.Scrollbar(statusFrame)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		#textLog
		self.textLog = tk.Text(statusFrame, wrap=tk.WORD, yscrollcommand=scrollbar.set, width=40, height=11)
		self.textLog.insert(tk.END, "Welcome to the iTruck app for the SLOPE project\n")	
		self.textLog.pack()
		scrollbar.config(command=self.textLog.yview)
			
		self.checkStatus()		#Checking if RFID, GPS and GPRS are ok
		self.loadXmlFile()		#Loading xml config file		
		self.updateLEDS()
		self.root.mainloop()	#execution line stops here		
				

	def updateLEDS(self):		
		if self.statusDeLeds == 'red':
			self.circleCanvasGPRS.create_oval(0,0,20,20, width=0, fill='green')
			self.circleCanvasGPS.create_oval(0,0,20,20, width=0, fill='green')
			#self.textLog.insert(tk.END, "LEDS changed to green")
			self.statusDeLeds='green'
		else:	
			self.circleCanvasGPRS.create_oval(0,0,20,20, width=0, fill='red')
			self.circleCanvasGPS.create_oval(0,0,20,20, width=0, fill='red')
			#self.textLog.insert(tk.END, "LEDS changed to red")
			self.statusDeLeds='red'
						
		self.root.after(1000, self.updateLEDS)


	def createConfigureWindow(self):
		topWindow=tk.Toplevel()
		topWindow.wm_title("Configuration")		
		
		lbl0=tk.Label(topWindow, text="TCP Reader Configuration").grid(row=0, column=0, padx=10, pady=2)				

		lbl1=tk.Label(topWindow, text="RFID Reader IP:").grid(row=1, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e1=tk.Entry(topWindow)
		self.e1.grid(row=1, column=1, padx=10, pady=2)
		self.e1.delete(0,tk.END)
		self.e1.insert(0,self.TCP_IP_RFID_READER)
		lbl2=tk.Label(topWindow, text="i.e. 192.168.0.20").grid(row=1, column=2, padx=10, pady=2, sticky=tk.W)				
		
		lbl3=tk.Label(topWindow, text="RFID Reader PORT:").grid(row=2, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e2=tk.Entry(topWindow)
		self.e2.grid(row=2, column=1, padx=10, pady=2)
		self.e2.delete(0,tk.END)
		self.e2.insert(0,self.TCP_PORT_RFID_READER)
		lbl4=tk.Label(topWindow, text="i.e. 2189").grid(row=2, column=2, padx=10, pady=2, sticky=tk.W)				
		
		lbl5=tk.Label(topWindow, text="TCP BUFFER:").grid(row=3, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e3=tk.Entry(topWindow)
		self.e3.grid(row=3, column=1, padx=10, pady=2)
		self.e3.delete(0,tk.END)
		self.e3.insert(0,self.BUFFER_SIZE_RFID_READER)					
		lbl6=tk.Label(topWindow, text="i.e. 512").grid(row=3, column=2, padx=10, pady=2, sticky=tk.W)				
			
		separator1=tk.Frame(topWindow, height=2, width=100, borderwidth=2, relief=tk.RAISED)		
		separator1.grid(row=4, columnspan=6, sticky=tk.W+tk.E, padx=10, pady=2)				
		
		lbl7=tk.Label(topWindow, text="RFID reader configuration").grid(row=5, column=0, padx=10, pady=2)				
		
		lbl8=tk.Label(topWindow, text="ATTRIB ANTS:").grid(row=6, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e4=tk.Entry(topWindow)
		self.e4.grid(row=6, column=1, padx=10, pady=2)
		self.e4.delete(0,tk.END)
		self.e4.insert(0,self.ATTRIB_ANTS)					
		cfgBtn1=tk.Button(topWindow, text='Info', command=self.cfgBtn1_click)
		cfgBtn1.grid(row=6, column=2, padx=10, pady=2, sticky=tk.W)

		lbl9=tk.Label(topWindow, text="ATTRIB TAGTYPE:").grid(row=6, column=3, padx=10, pady=2, sticky=tk.W)				
		self.e5=tk.Entry(topWindow)
		self.e5.grid(row=6, column=4, padx=10, pady=2)
		self.e5.delete(0,tk.END)
		self.e5.insert(0,self.ATTRIB_TAGTYPE)					
		cfgBtn2=tk.Button(topWindow, text='Info', command=self.cfgBtn2_click)
		cfgBtn2.grid(row=6, column=5, padx=10, pady=2, sticky=tk.W)

		lbl10=tk.Label(topWindow, text="ATTRIB FIELDSTRENGTH:").grid(row=7, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e6=tk.Entry(topWindow)
		self.e6.grid(row=7, column=1, padx=10, pady=2)
		self.e6.delete(0,tk.END)
		self.e6.insert(0,self.ATTRIB_FIELDSTRENGTH)					
		cfgBtn3=tk.Button(topWindow, text='Info', command=self.cfgBtn3_click)
		cfgBtn3.grid(row=7, column=2, padx=10, pady=2, sticky=tk.W)
		
		lbl11=tk.Label(topWindow, text="ATTRIB RDTRIES:").grid(row=7, column=3, padx=10, pady=2, sticky=tk.W)				
		self.e7=tk.Entry(topWindow)
		self.e7.grid(row=7, column=4, padx=10, pady=2)
		self.e7.delete(0,tk.END)
		self.e7.insert(0,self.ATTRIB_RDTRIES)					
		cfgBtn4=tk.Button(topWindow, text='Info', command=self.cfgBtn4_click)
		cfgBtn4.grid(row=7, column=5, padx=10, pady=2, sticky=tk.W)
		
		lbl12=tk.Label(topWindow, text="ATTRIB RPTTIMEOUT:").grid(row=8, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e8=tk.Entry(topWindow)
		self.e8.grid(row=8, column=1, padx=10, pady=2)
		self.e8.delete(0,tk.END)
		self.e8.insert(0,self.ATTRIB_RPTTIMEOUT)					
		cfgBtn5=tk.Button(topWindow, text='Info', command=self.cfgBtn5_click)
		cfgBtn5.grid(row=8, column=2, padx=10, pady=2, sticky=tk.W)
		
		lbl13=tk.Label(topWindow, text="ATTRIB IDTIMEOUT:").grid(row=8, column=3, padx=10, pady=2, sticky=tk.W)				
		self.e9=tk.Entry(topWindow)
		self.e9.grid(row=8, column=4, padx=10, pady=2)
		self.e9.delete(0,tk.END)
		self.e9.insert(0,self.ATTRIB_IDTIMEOUT)					
		cfgBtn6=tk.Button(topWindow, text='Info', command=self.cfgBtn6_click)
		cfgBtn6.grid(row=8, column=5, padx=10, pady=2, sticky=tk.W)

		lbl13=tk.Label(topWindow, text="ATTRIB ANTTIMEOUT:").grid(row=9, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e10=tk.Entry(topWindow)
		self.e10.grid(row=9, column=1, padx=10, pady=2)
		self.e10.delete(0,tk.END)
		self.e10.insert(0,self.ATTRIB_ANTTIMEOUT)					
		cfgBtn7=tk.Button(topWindow, text='Info', command=self.cfgBtn7_click)
		cfgBtn7.grid(row=9, column=2, padx=10, pady=2, sticky=tk.W)
		
		lbl14=tk.Label(topWindow, text="ATTRIB IDTRIES:").grid(row=9, column=3, padx=10, pady=2, sticky=tk.W)				
		self.e11=tk.Entry(topWindow)
		self.e11.grid(row=9, column=4, padx=10, pady=2)
		self.e11.delete(0,tk.END)
		self.e11.insert(0,self.ATTRIB_IDTRIES)					
		cfgBtn8=tk.Button(topWindow, text='Info', command=self.cfgBtn8_click)
		cfgBtn8.grid(row=9, column=5, padx=10, pady=2, sticky=tk.W)

		lbl15=tk.Label(topWindow, text="ATTRIB ANTTRIES:").grid(row=10, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e12=tk.Entry(topWindow)
		self.e12.grid(row=10, column=1, padx=10, pady=2)
		self.e12.delete(0,tk.END)
		self.e12.insert(0,self.ATTRIB_ANTTRIES)					
		cfgBtn9=tk.Button(topWindow, text='Info', command=self.cfgBtn9_click)
		cfgBtn9.grid(row=10, column=2, padx=10, pady=2, sticky=tk.W)
		
		lbl16=tk.Label(topWindow, text="ATTRIB WRTRIES:").grid(row=10, column=3, padx=10, pady=2, sticky=tk.W)				
		self.e13=tk.Entry(topWindow)
		self.e13.grid(row=10, column=4, padx=10, pady=2)
		self.e13.delete(0,tk.END)
		self.e13.insert(0,self.ATTRIB_WRTRIES)					
		cfgBtn10=tk.Button(topWindow, text='Info', command=self.cfgBtn10_click)
		cfgBtn10.grid(row=10, column=5, padx=10, pady=2, sticky=tk.W)

		lbl17=tk.Label(topWindow, text="ATTRIB LOCKTRIES:").grid(row=11, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e14=tk.Entry(topWindow)
		self.e14.grid(row=11, column=1, padx=10, pady=2)
		self.e14.delete(0,tk.END)
		self.e14.insert(0,self.ATTRIB_LOCKTRIES)					
		cfgBtn11=tk.Button(topWindow, text='Info', command=self.cfgBtn11_click)
		cfgBtn11.grid(row=11, column=2, padx=10, pady=2, sticky=tk.W)
		
		lbl18=tk.Label(topWindow, text="ATTRIB SELTRIES:").grid(row=11, column=3, padx=10, pady=2, sticky=tk.W)				
		self.e15=tk.Entry(topWindow)
		self.e15.grid(row=11, column=4, padx=10, pady=2)
		self.e15.delete(0,tk.END)
		self.e15.insert(0,self.ATTRIB_SELTRIES)					
		cfgBtn12=tk.Button(topWindow, text='Info', command=self.cfgBtn12_click)
		cfgBtn12.grid(row=11, column=5, padx=10, pady=2, sticky=tk.W)				
	
		lbl19=tk.Label(topWindow, text="ATTRIB UNSELTRIES:").grid(row=12, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e16=tk.Entry(topWindow)
		self.e16.grid(row=12, column=1, padx=10, pady=2)
		self.e16.delete(0,tk.END)
		self.e16.insert(0,self.ATTRIB_UNSELTRIES)					
		cfgBtn13=tk.Button(topWindow, text='Info', command=self.cfgBtn13_click)
		cfgBtn13.grid(row=12, column=2, padx=10, pady=2, sticky=tk.W)
		
		lbl20=tk.Label(topWindow, text="ATTRIB INITTRIES:").grid(row=12, column=3, padx=10, pady=2, sticky=tk.W)				
		self.e17=tk.Entry(topWindow)
		self.e17.grid(row=12, column=4, padx=10, pady=2)
		self.e17.delete(0,tk.END)
		self.e17.insert(0,self.ATTRIB_INITTRIES)					
		cfgBtn14=tk.Button(topWindow, text='Info', command=self.cfgBtn14_click)
		cfgBtn14.grid(row=12, column=5, padx=10, pady=2, sticky=tk.W)		

		lbl21=tk.Label(topWindow, text="ATTRIB INITIALQ:").grid(row=13, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e18=tk.Entry(topWindow)
		self.e18.grid(row=13, column=1, padx=10, pady=2)
		self.e18.delete(0,tk.END)
		self.e18.insert(0,self.ATTRIB_INITIALQ)					
		cfgBtn15=tk.Button(topWindow, text='Info', command=self.cfgBtn15_click)
		cfgBtn15.grid(row=13, column=2, padx=10, pady=2, sticky=tk.W)
		
		lbl22=tk.Label(topWindow, text="ATTRIB QUERYSEL:").grid(row=13, column=3, padx=10, pady=2, sticky=tk.W)				
		self.e19=tk.Entry(topWindow)
		self.e19.grid(row=13, column=4, padx=10, pady=2)
		self.e19.delete(0,tk.END)
		self.e19.insert(0,self.ATTRIB_QUERYSEL)					
		cfgBtn16=tk.Button(topWindow, text='Info', command=self.cfgBtn16_click)
		cfgBtn16.grid(row=13, column=5, padx=10, pady=2, sticky=tk.W)

		lbl23=tk.Label(topWindow, text="ATTRIB QUERYTARGET:").grid(row=14, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e20=tk.Entry(topWindow)
		self.e20.grid(row=14, column=1, padx=10, pady=2)
		self.e20.delete(0,tk.END)
		self.e20.insert(0,self.ATTRIB_QUERYTARGET)					
		cfgBtn17=tk.Button(topWindow, text='Info', command=self.cfgBtn17_click)
		cfgBtn17.grid(row=14, column=2, padx=10, pady=2, sticky=tk.W)
		
		lbl24=tk.Label(topWindow, text="ATTRIB SESSION:").grid(row=14, column=3, padx=10, pady=2, sticky=tk.W)				
		self.e21=tk.Entry(topWindow)
		self.e21.grid(row=14, column=4, padx=10, pady=2)
		self.e21.delete(0,tk.END)
		self.e21.insert(0,self.ATTRIB_SESSION)					
		cfgBtn18=tk.Button(topWindow, text='Info', command=self.cfgBtn18_click)
		cfgBtn18.grid(row=14, column=5, padx=10, pady=2, sticky=tk.W)

		lbl25=tk.Label(topWindow, text="ATTRIB LBTCHANNEL:").grid(row=15, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e22=tk.Entry(topWindow)
		self.e22.grid(row=15, column=1, padx=10, pady=2)
		self.e22.delete(0,tk.END)
		self.e22.insert(0,self.ATTRIB_LBTCHANNEL)					
		cfgBtn19=tk.Button(topWindow, text='Info', command=self.cfgBtn19_click)
		cfgBtn19.grid(row=15, column=2, padx=10, pady=2, sticky=tk.W)
		
		lbl26=tk.Label(topWindow, text="ATTRIB SCHEDULEOPT:").grid(row=15, column=3, padx=10, pady=2, sticky=tk.W)				
		self.e23=tk.Entry(topWindow)
		self.e23.grid(row=15, column=4, padx=10, pady=2)
		self.e23.delete(0,tk.END)
		self.e23.insert(0,self.ATTRIB_SCHEDULEOPT)					
		cfgBtn20=tk.Button(topWindow, text='Info', command=self.cfgBtn20_click)
		cfgBtn20.grid(row=15, column=5, padx=10, pady=2, sticky=tk.W)
		
		lbl27=tk.Label(topWindow, text="ATTRIB FIELDSEP:").grid(row=16, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e24=tk.Entry(topWindow)
		self.e24.grid(row=16, column=1, padx=10, pady=2)
		self.e24.delete(0,tk.END)
		self.e24.insert(0,self.ATTRIB_FIELDSEP)					
		cfgBtn21=tk.Button(topWindow, text='Info', command=self.cfgBtn21_click)
		cfgBtn21.grid(row=16, column=2, padx=10, pady=2, sticky=tk.W)
		
		lbl28=tk.Label(topWindow, text="ATTRIB BROADCASTSYNC:").grid(row=16, column=3, padx=10, pady=2, sticky=tk.W)				
		self.e25=tk.Entry(topWindow)
		self.e25.grid(row=16, column=4, padx=10, pady=2)
		self.e25.delete(0,tk.END)
		self.e25.insert(0,self.ATTRIB_BROADCASTSYNC)					
		cfgBtn22=tk.Button(topWindow, text='Info', command=self.cfgBtn22_click)
		cfgBtn22.grid(row=16, column=5, padx=10, pady=2, sticky=tk.W)

		lbl29=tk.Label(topWindow, text="ATTRIB UTCTIME:").grid(row=17, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e26=tk.Entry(topWindow)
		self.e26.grid(row=17, column=1, padx=10, pady=2)
		self.e26.delete(0,tk.END)
		self.e26.insert(0,self.ATTRIB_UTCTIME)					
		cfgBtn23=tk.Button(topWindow, text='Info', command=self.cfgBtn23_click)
		cfgBtn23.grid(row=17, column=2, padx=10, pady=2, sticky=tk.W)
		
		lbl30=tk.Label(topWindow, text="ATTRIB TIMEOUTMODE:").grid(row=17, column=3, padx=10, pady=2, sticky=tk.W)				
		self.e27=tk.Entry(topWindow)
		self.e27.grid(row=17, column=4, padx=10, pady=2)
		self.e27.delete(0,tk.END)
		self.e27.insert(0,self.ATTRIB_TIMEOUTMODE)					
		cfgBtn24=tk.Button(topWindow, text='Info', command=self.cfgBtn24_click)
		cfgBtn24.grid(row=17, column=5, padx=10, pady=2, sticky=tk.W)

		lbl31=tk.Label(topWindow, text="ATTRIB NOTAGRPT:").grid(row=18, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e28=tk.Entry(topWindow)
		self.e28.grid(row=18, column=1, padx=10, pady=2)
		self.e28.delete(0,tk.END)
		self.e28.insert(0,self.ATTRIB_NOTAGRPT)					
		cfgBtn25=tk.Button(topWindow, text='Info', command=self.cfgBtn25_click)
		cfgBtn25.grid(row=18, column=2, padx=10, pady=2, sticky=tk.W)
		
		lbl32=tk.Label(topWindow, text="ATTRIB IDREPORT:").grid(row=18, column=3, padx=10, pady=2, sticky=tk.W)				
		self.e29=tk.Entry(topWindow)
		self.e29.grid(row=18, column=4, padx=10, pady=2)
		self.e29.delete(0,tk.END)
		self.e29.insert(0,self.ATTRIB_IDREPORT)					
		cfgBtn26=tk.Button(topWindow, text='Info', command=self.cfgBtn26_click)
		cfgBtn26.grid(row=18, column=5, padx=10, pady=2, sticky=tk.W)
		
		lbl33=tk.Label(topWindow, text="ATTRIB SCHEDOPT:").grid(row=19, column=0, padx=10, pady=2, sticky=tk.W)				
		self.e30=tk.Entry(topWindow)
		self.e30.grid(row=19, column=1, padx=10, pady=2)
		self.e30.delete(0,tk.END)
		self.e30.insert(0,self.ATTRIB_SCHEDOPT)					
		cfgBtn27=tk.Button(topWindow, text='Info', command=self.cfgBtn27_click)
		cfgBtn27.grid(row=19, column=2, padx=10, pady=2, sticky=tk.W)
	
		lblExample=tk.Label(topWindow, text="Example:").grid(row=20, column=0, padx=10, pady=2, sticky=tk.W)				
		self.tExample = tk.Text(topWindow, wrap=tk.WORD, height=1)
		self.tExample.grid(row=20, column=1, columnspan=5, padx=10, pady=2, sticky=tk.W+tk.E)
		
		lblDescription=tk.Label(topWindow, text="Description:").grid(row=21, column=0, padx=10, pady=2, sticky=tk.W)				
		self.tDescription = tk.Text(topWindow, wrap=tk.WORD, height=1)
		self.tDescription.grid(row=21, column=1, columnspan=5, padx=10, pady=2, sticky=tk.W+tk.E)

		separator2=tk.Frame(topWindow, height=2, width=100, borderwidth=2, relief=tk.RAISED)		
		separator2.grid(row=22, columnspan=6, sticky=tk.W+tk.E, padx=10, pady=2)	
		
		genXML=tk.Button(topWindow, text='Save XML', command=self.saveXmlFile)
		genXML.grid(row=23, column=1, padx=10, pady=4, sticky=tk.W+tk.E)				

		exitTopWindow=tk.Button(topWindow, text='Exit', command=topWindow.destroy)
		exitTopWindow.grid(row=23, column=4, padx=10, pady=4, sticky=tk.W+tk.E)		
	
	
	def sendTestCommand(self):
		
		command= self.eTestRfid.get()+'\n'
		self.textLog.insert(tk.END, "sending command: " + command )			
		response = self.sendSingleBriCommand(command)
		newResponse=response.replace('\r','')
		self.textLog.insert(tk.END, newResponse)				
		self.textLog.yview(tk.END)  #to keep the last text always visible
		
	
	def sendReadCommand(self):		
		command= self.eTestRfid.get()+'\n'
		self.textLog.insert(tk.END, "sending command: " + command )			
		response = self.sendSingleBriCommand(command)
		newResponse=response.replace('\r','')
		self.textLog.insert(tk.END, newResponse)				
		self.textLog.yview(tk.END)  #to keep the last text always visible
	

	def sendSingleBriCommand(self, command):
		 
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#self.textLog.insert(tk.END,'socket created\n')   
			s.connect((self.TCP_IP_RFID_READER, self.TCP_PORT_RFID_READER))
			#self.textLog.insert(tk.END,'socket connected\n')   		
			s.send(command.encode('utf-8'))
			#self.textLog.insert(tk.END,'message sent succesfuly\n')  
			responseAsByte=s.recv(self.BUFFER_SIZE_RFID_READER)
			#self.textLog.insert(tk.END,'message received succesffuly\n') 
			s.close()  
			responseAsString=responseAsByte.decode('utf-8')
		
		except:
			s.close()	
			responseAsString= "exception when doing "+ command
		
		finally:
			return responseAsString
			
			
	def saveXmlFile(self):
		
		config=ET.Element("config")
		
		TcpReaderConfig=ET.SubElement(config, "TcpReaderConfig")	
		
		ET_TCP_IP_RFID_READER=ET.SubElement(TcpReaderConfig, "TCP_IP_RFID_READER")	
		ET_TCP_IP_RFID_READER.text=(self.e1.get())
		self.TCP_IP_RFID_READER=(self.e1.get())
	
		ET_TCP_PORT_RFID_READER=ET.SubElement(TcpReaderConfig, "TCP_PORT_RFID_READER")	
		ET_TCP_PORT_RFID_READER.text=(self.e2.get())
		self.TCP_PORT_RFID_READER=int((self.e2.get()))
				
		ET_BUFFER_SIZE_RFID_READER=ET.SubElement(TcpReaderConfig, "BUFFER_SIZE_RFID_READER")	
		ET_BUFFER_SIZE_RFID_READER.text=(self.e3.get())	
		self.BUFFER_SIZE_RFID_READER=int((self.e3.get()))		
		
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
		
		self.textLog.insert(tk.END, "Xml file generated succcessfully\n")
		self.textLog.yview(tk.END)  #to keep the last text always visible


	def checkStatus(self):
		
		#check RFID reader status
		command= 'briver\n'		
		response= self.sendSingleBriCommand(command)	
		newResponse=response[6:8] #Here we remove all answered text except from where OK is placed
		
		if newResponse =="OK":	 #to change from byte to utf-8		
			self.circleCanvasRFID.create_oval(0,0,20,20, width=0, fill='green')
			self.textLog.insert(tk.END, 'RFID reader OK \n')				
			self.textLog.yview(tk.END)  #to keep the last text always visible
		else:
			self.circleCanvasRFID.create_oval(0,0,20,20, width=0, fill='red')
			self.textLog.insert(tk.END, 'RFID reader NOT OK \n')				
			self.textLog.yview(tk.END)  #to keep the last text always visible
			
			
	def loadXmlFile(self):
		
		#here we try to connecto to the xml file		
		try:
			tree=ET.parse('config.xml')
			XMLroot=tree.getroot()
			self.textLog.insert(tk.END, "Config file found\n")	
		except:	
			self.textLog.insert(tk.END, "Config file not found\n")

		#TCP Congiguration Info		
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
		
		self.textLog.insert(tk.END, "Xml file loaded successfully\n")
		self.textLog.yview(tk.END)  #to keep the last text always visible
			
			
	def terminate(self):
		self.root.destroy()
		

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
						
		
#main loop 
# if __name__  works ok in a direct execution. However, if the file is executed from another module, it is not executed
# that allows the other module to use de defined functions in this file without problems 
if __name__== '__main__':	
	myApp1=myTkinterApp()
	
