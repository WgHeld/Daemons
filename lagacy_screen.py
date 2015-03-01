#!/usr/bin/python

from httplib2 import Http
from requests.exceptions import ConnectionError
import json
import time
import serial
import random
import math


SERVER = "http://192.168.178.115"
PORT = 3000
CONFIG = {  
	    'clemens': 165,
	    'tobi': 130,
	    'christoph': 90,
	    'roby': 50
	}

def get_leader(json):
    points = 0
    leader = ""
    for p in json:
	up = int(p["points"])
	if (points < up):
	    points = up
	    leader = p["reference"]

    return leader;


last_angle = -1
def point_to(ser,angle):
    global last_angle
    if (last_angle == -1):
	last_angle = angle

    walk = math.fabs(last_angle - angle)
    astr = "%0.3d" % angle
    if (ser != ""):
	for i in range(0,3):
	    ser.write(astr[i])

    time.sleep(walk/10.0)
    print "Go to angle:"+astr 


def shuffle_seq(ser):
    point_to(ser,random.randint(1,90))
    point_to(ser,random.randint(90,180))


if __name__ == "__main__":
    
    url=SERVER+":"+str(PORT)+"/client/users"
    last_leader = ""
    ser = serial.Serial('/dev/ttyACM3', 9600)
    #ser ="" 

    while True:

	try:
	    ret,response = Http().request(url, method="GET")
	except:
	    print "Server:"+url+" gone?"
	    time.sleep(1);
	    continue
    
	leader = get_leader(json.loads(response))
	point_to(ser,CONFIG[leader])
#	if (leader != last_leader):
#	    shuffle_seq(ser);
#	    point_to(ser,CONFIG[leader])
#	    last_leader = leader

	print "Leader is:" + leader 
	time.sleep(1)


