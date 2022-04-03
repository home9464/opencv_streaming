"""
https://github.com/Bhagyarsh/usim800

https://github.com/Bhagyarsh/usim800/blob/master/usim800/Request/Request.py

https://community.element14.com/technologies/internet-of-things/f/forum/1499/gprs-module-http-get-post

"""

from usim800 import sim800
import json
gsm = sim800(baudrate=115200,path="/dev/serial0")
gsm.requests.APN = 'fast.t-mobile.com'
#gsm.requests.get(url="http://my-json-server.typicode.com/typicode/demo/posts")
#gsm.requests.get(url="http://www.1genomics.com")
r = gsm.requests
print(r.content)

#gsm.sms.send("1234567890","hi there")

data = {
    "lon": 123.456,
    "lat":234.567
}

# use WiFi
requests.post('http://10.0.0.4:8080/locations', json=data)

# use GSM
gsm.requests.post(url="http://10.0.0.4:8080/locations", data=json.dumps(data))
