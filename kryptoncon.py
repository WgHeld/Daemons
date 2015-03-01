import json
from httplib2 import Http
import time
from requests.exceptions import ConnectionError

SERVER = "http://192.168.178.115"
PORT = 3000
#SERVER = "https://wgheld-krypto.herokuapp.com"
#PORT = 443

class KryptonCon:

    server=""
    port=0
    devid=""

    def __init__(self, devid, server=SERVER, port=PORT):
	self.devid = devid
	self.server = server
	self.port = port

    def req(self, url, data):
	data['device'] = self.devid;
	headers = {'content-type': 'application/json'}
	url=self.server+":"+str(self.port)+url
	for x in range(0,5):
	    try:
		return Http().request(url, method="POST", headers=headers, body=json.dumps(data));
	    except:
		print("Connection to '"+url+"' refused try: " + str(x))
	return "ERROR"

    def start_msg(self, userid=""):
        print("sendig start %s"%self.devid)
	url = "/api/events/start"
	return self.req(url,  {'user': userid});
    
    def end_msg(self, userid=""):
        print("sendig end %s"%self.devid)
	url = "/api/events/end"
	return self.req(url,  {'user': userid});
