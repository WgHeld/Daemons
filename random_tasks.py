from kryptoncon import KryptonCon
import time
import signal
import random

IDLE=0
WAIT_FOR_USER=1
#serverip="https://wgheld-krypto.herokuapp.com"
serverip="http://192.168.178.115"
#port=443
port=3000

class FakeSensor:
    con = ""
    devid=""
    state=IDLE
    next_state_change = 0

    def __init__(self, devid):
	self.devid = devid
	self.next_state_change = self.get_next_time()
	self.con = KryptonCon(devid,serverip,port);

    def get_next_time(self):
	#if (self.state == IDLE):
	#return time.time() + random.randint(20, 50);
	rand = time.time() + random.randint(2, 10);
	return rand

    def get_random_user(self):
	names = ['Tobi', 'Clemens', 'Christoph', 'Roby'];
	return names[random.randint(0,3)]

    def run(self):
	if (time.time() > self.next_state_change):
	    self.next_state()
	
    def next_state(self):
	print (self.devid + " State: "+ str(self.state))
	if (self.state == IDLE):
	    self.con.start_msg()
	    self.next_state_change = self.get_next_time()
	    self.state = WAIT_FOR_USER
	elif (self.state == WAIT_FOR_USER):
	    self.con.end_msg(self.get_random_user())
	    self.next_state_change = self.get_next_time() 
	    self.state = IDLE

def onSignal(signum, frame):
    print "Bye Bye!\n"
    sys.exit(1)

DISHWASHER_ID  = '89287aad-db10-4303-ad01-5547c67eca96' #to set to 'f4ab513e-590d-494f-8586-2e06af2d186d'
LIGHT_ID       = '103156b3-1a78-42c2-a4af-1512721ded3d'
BRIDGE_ID      = 'ada09702-5898-42fb-9c42-7ef0c1a1dd45'
THERMOMETER_ID = 'a7ec5e46-4f6e-4193-a21a-5b5c7cb34485'
GYROSCOPE_ID   = 'a2e4d803-82d2-4504-add2-8e99111d9178'
INFRARED_ID    = 'ac8f56f3-9ccc-4896-b2e0-a5a9fc7e603b'
MICROPHONE_ID  = '89287aad-db10-4303-ad01-5547c67eca96'


if __name__ == "__main__":

    signal.signal(signal.SIGINT, onSignal)
    signal.signal(signal.SIGTERM, onSignal)
    random.seed()

    l = []
    l.append( FakeSensor(DISHWASHER_ID))
##    l.append( FakeSensor(BRIDGE_ID))
    l.append( FakeSensor(LIGHT_ID))

    while True:
	for fs in l:
	    fs.run()
	print "Run..."
	time.sleep(1)
    
    
