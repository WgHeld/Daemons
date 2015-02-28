import json
from httplib2 import Http
import time
from requests.exceptions import ConnectionError

class KryptonCon:

    server=""
    port=0
    devid=""

    def __init__(self, devid, server="https://wgheld-krypto.herokuapp.com", port=443):
	self.devid = devid
	self.server = server
	self.port = port

    def req(self, url, data):
	data['device'] = self.devid;
	headers = {'content-type': 'application/json'}
	url=self.server+":"+str(self.port)+url
	for x in range(0,5):
	    try:
		Http().request(url, method="POST", headers=headers, body=json.dumps(data));
		return
	    except:
		print("Connection to '"+url+"' refused try: " + str(x))


    def start_msg(self, userid=""):
	url = "/api/events/start"
	self.req(url,  {'user': userid});
    
    def end_msg(self, userid=""):
	url = "/api/events/end"
	self.req(url,  {'user': userid});
