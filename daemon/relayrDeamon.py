#!/usr/bin/env python

import sys, time
from daemon import Daemon
from sensor import Sensor

ACCESS_TOKEN = '74_4C9xsAyFNKreiCONSb1YvgDz7jNTF'
DISHWASHER_ID  = '89287aad-db10-4303-ad01-5547c67eca96' #to set to 'f4ab513e-590d-494f-8586-2e06af2d186d'
LIGHT_ID       = '103156b3-1a78-42c2-a4af-1512721ded3d'
BRIDGE_ID      = 'ada09702-5898-42fb-9c42-7ef0c1a1dd45'
THERMOMETER_ID = 'a7ec5e46-4f6e-4193-a21a-5b5c7cb34485'
GYROSCOPE_ID   = 'a2e4d803-82d2-4504-add2-8e99111d9178'
INFRARED_ID    = 'ac8f56f3-9ccc-4896-b2e0-a5a9fc7e603b'
MICROPHONE_ID  = '89287aad-db10-4303-ad01-5547c67eca96'

class RelayrDaemon(Daemon):

    sensors = []

#    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
#        "..."
        

    def add(self, sensor, callback):
        "Add the sensor to the list"
        
        sensorEntry = (sensor,callback)
        self.sensors.append(sensorEntry)
        
        
    def connectAll(self):
        "Connect all sensors added to the daemon"
        
        for s in self.sensors:
            s[0].connect()


    def disconnectAll(self):
        "Disconnect all sensors added to the daemon"
        
        for s in self.sensors:
            s[0].disconnect()
        
        
    def run(self):
        "Every 5 seconds it check the data from the sensor and..."
        
        for s in self.sensors:
            s[1](s[0])

        time.sleep(5);
        
def printData(sensor):
    print sensor.name + " - " + sensor.level

if __name__ == "__main__":
    daemon = RelayrDaemon('/tmp/daemon-example.pid')
    
    if not daemon.sensors:
        proximity = Sensor("proximity",ACCESS_TOKEN,LIGHT_ID,"prox")
        dishwasher = Sensor("dishwasher",ACCESS_TOKEN,DISHWASHER_ID,"snd_level")
        dishwasher = Sensor("dishwasher",ACCESS_TOKEN,DISHWASHER_ID,"noiseLevel",Sensor.CONNTYPE_MQTT)
        daemon.add(proximity,printData)
        daemon.add(dishwasher,printData)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.connectAll()
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
            daemon.disconnectAll()
        #elif 'restart' == sys.argv[1]:
        #    daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
