# This project aims to learn to use webservices with python
# Started in 09-apr-2015

import httplib2


h = httplib2.Http('.cache')

response, content = h.request('http://diveintopython3.org/examples/feed.xml')
print (response.status)

print (str(content))



