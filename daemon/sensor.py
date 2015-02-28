#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example script using the Wunderbar over the Relayr cloud.

This will connect to a proximity, read its level and send
an email notification to some receiver if that noise level exceeds
a certain threshold.
"""

import sys
import json
import time
import os

from relayr import Client
from relayr.dataconnection import MqttStream

class Sensor(object):
    CONNTYPE_STD = "std"
    CONNTYPE_MQTT = "mqtt"

    level = "Not setted"
    log = []
    
    def __init__(self, name, token, dev_id, param, connType=CONNTYPE_STD):
        self.name   = name
        self.token  = token
        self.dev_id = dev_id
        self.param  = param
        self.connType = connType
        
        
    def connect(self):
        "Connect to a device and start read data."

        client = Client(token=self.token)
        device = client.get_device(id=self.dev_id).get_info()
        user = client.get_user()
        app = client.get_app()
        if self.connType == self.CONNTYPE_STD:
            self.conn = user.connect_device(app, device, self.call)
        elif self.connType == self.CONNTYPE_MQTT:
            self.conn = MqttStream(self.call, [device])
        self.conn.start()
        
        
    def disconnect(self):
        "Disconnect to a device and stop to read data."

        #if not self.conn
            #exit
        
        self.conn.stop()
        

    def call(self, first, second):
    #       (self, message, channel): STD
    #       (self, url, message): MQTT
        "Called when data are recived from sensor."
        "This function set last value on self.level and add it to self.log list"
        if self.connType == self.CONNTYPE_STD:
            message = first
            value = json.loads(message)[self.param]
        elif self.connType == self.CONNTYPE_MQTT:
            message = second
            for element in json.loads(message)['readings']:
                if element['meaning'] == self.param:
                    value = element['value']
        self.level = value
        logEntry = (self.level,time.time())
        self.log.append(logEntry)
        #debug#print "Recived data from device"
        #debug#print self.level


"""
Test main function:

Print the proximity value every half second for 20 times then
print all log entries before exit.

NB: Check if the value don't change during the monitored 10
    seconds the script don't recive any value. 
"""
ACCESS_TOKEN = '74_4C9xsAyFNKreiCONSb1YvgDz7jNTF'
LIGHT_ID       = '103156b3-1a78-42c2-a4af-1512721ded3d'
DISHWASHER_ID  = '89287aad-db10-4303-ad01-5547c67eca96' #to set to 'f4ab513e-590d-494f-8586-2e06af2d186d'

if __name__ == "__main__":
#    proximity = Sensor("proximity",ACCESS_TOKEN,LIGHT_ID,"prox")
    proximity = Sensor("dishwasher",ACCESS_TOKEN,DISHWASHER_ID,"snd_level")
#    proximity = Sensor("dishwasher",ACCESS_TOKEN,DISHWASHER_ID,"noiseLevel",Sensor.CONNTYPE_MQTT)
    proximity.connect()
    
    for i in range(1,200):
        print proximity.level
        time.sleep(0.5)
    
    if not proximity.log:
        print "No log recorded"
    else:
        for entry in proximity.log:
            print entry
        


