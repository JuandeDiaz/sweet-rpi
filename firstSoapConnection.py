# This project aims to learn to use webservices with python
# This connects to a websevice provided by ITENE in the FREVUE website
# File started in 09-apr-2015

import pysimplesoap
from pysimplesoap.simplexml import SimpleXMLElement

import logging
import sys

# This is in case we want to debug the received info
logging.basicConfig()

# variables
soapUrl="http://95.60.252.45/webservices/wsgetcandata.asmx"
namespace="http://tempuri.org/"
SoapAction="http://tempuri.org/"

# This created a conection object to the soap webservice
# Change trace to True if you want to debug
mySoapClient = pysimplesoap.client.SoapClient(location=soapUrl+'?wsdl', action=SoapAction, namespace=namespace, trace=False)

# The received response object is a type pysimplesoap.client.SimpleXMLElement
response= mySoapClient.GetDevicesAlias(company="CALIDADPASCUAL", userName="administrador", password="p@ssw0rd")

print ('How many detected devices?')
print (len(response.Devices))

print ('\nHow many alias received?')
print (len(response.alias))

print ('\nWhat is the first alias?')
print (response.alias(0))

print ('\nWhat is the second alias?')
print (response.alias(1))

print ('\nWhat is the object repr?')
print (repr(response))

print ('\nWhat is the object xml?')
print (response.as_xml())

#uncomment this to create a xml file 
print ('\nCreating xml file')
#text_file = open ("receivedXml.xml", "w")
#text_file.write(response.as_xml().decode("utf-8"))  #decoding is needed to change from byte to string
#text_file.close()
