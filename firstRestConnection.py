import requests

#SLOPE address which allows rest communication
url='https://slopefis.mhgsystems.com/slope-fis/rest/customers/'

headers ={'Accept':'application/json'}
#headers ={'Accept':'application/xml'}

if __name__=='__main__':
	
	r=requests.get(url, headers=headers, auth=('test','test'), verify=False)
	
	# this 
	print(r.status_code)
	
	print(r.headers)

	print(r.text)
