#!/usr/bin/python

#
# sudo pip install -U git+https://github.com/relayr/python-sdk
#
import json
import relayr 
import time
from relayr import Client
from relayr.dataconnection import MqttStream

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

DO_DBG_CONSOLE=False
DO_DBG_LOGFILE=True

WG_TOKEN='Pm8az.iBVc6DBdHI7iKI9KDFu-VdKW4_'

KUECHE='637c568c-a48c-4282-ad5e-20993f6efb51'
DISHWASHER='f4ab513e-590d-494f-8586-2e06af2d186d'
INFRARED='ac8f56f3-9ccc-4896-b2e0-a5a9fc7e603b'
GYROSCOPE='a2e4d803-82d2-4504-add2-8e99111d9178'
MICROPHONE='89287aad-db10-4303-ad01-5547c67eca96' 
THERMOMETER='a7ec5e46-4f6e-4193-a21a-5b5c7cb34485' 
LIGHT='103156b3-1a78-42c2-a4af-1512721ded3d'
BRIDGE='ada09702-5898-42fb-9c42-7ef0c1a1dd45' 

def empty_trans_fn(state, sensor_val):
    machine = state.machine
    if (sensor_val > 200):
        if state.condition_met_long_enouph():
            machine.set_state( machine.half_full ) 
    else:
        state.reset_state()


def half_full_trans_fn(state, sensor_val):
    machine = state.machine
    if (sensor_val > 1500):
        if state.condition_met_long_enouph():
            machine.set_state( machine.full ) 
    else:
        state.reset_state()


def full_trans_fn(state, sensor_val):
    machine = state.machine
    if (sensor_val < 100):
        if state.condition_met_long_enouph():
            machine.set_state( machine.empty ) 
    else:
        state.reset_state()


class State():
    def __init__( self, machine, name, trans_func, condition_time=5 ):
        self.machine = machine
        self.name = name
        self.trans_func = trans_func
        self.condition_time = condition_time

    def condition_met_long_enouph(self):
        now = int(time.time())

        if self.cond_met_since == 0:
            self.cond_met_since = now
            
        if now > self.cond_met_since + self.condition_time:
            print("condition met long enough %s"%self.name)
            return True

        print("need more time %s"%self.name)
        return False

    def reset_state(self):
        print("reset state %s"%self.name)
        self.cond_met_since = 0


class TrashMachine():

    def __init__(self):
        self.empty         = State(self, 'empty'      , empty_trans_fn)
        self.half_full     = State(self, 'half_full'  , half_full_trans_fn)
        self.full          = State(self, 'full'       , full_trans_fn)
        self.set_state( self.empty )

    def machine_step(self, sensor_val):
        self.current_state.trans_func( self.current_state, sensor_val )

    def set_state(self, state):
        state.reset_state()
        self.current_state = state
        print("entering_state: %s"%state.name)


def dbg_rapi(msg):
    if DO_DBG_CONSOLE:
        print(msg)
    if DO_DBG_LOGFILE:
        logfile = open("logfile", 'a')
        logfile.write("%s\n"%msg)
        logfile.close()

def distance_callback(topic, payload):
    dbg_rapi(payload)
    readings = json.loads(payload)["readings"]
    for element in readings:
        if element["meaning"] == 'proximity':
            distance = element['value'];
            print(distance)
            trash_machine.machine_step(distance)


def list_all_devices(usr):
    devs = usr.get_devices()
    for d in devs:
        info = d.get_info()
        print("dev '%s' (%s) " % (info.name, info.id))

def toggle_led_all_devices(usr):
    devs = usr.get_devices()
    for d in devs:
        d.switch_led_on(True)

trash_machine = TrashMachine()

c = relayr.Client(token=WG_TOKEN)
usr = c.get_user()
#list_all_devices(usr)
dev = c.get_device(id=LIGHT)
app = c.get_app()
dbg_rapi(app)

stream = MqttStream(distance_callback, [dev])
stream.start()

while True:
    print("Daemon is still running :-) '%s' (%s)..." % (dev.get_info().name, dev.get_info().id))
    time.sleep(600)

stream.stop()




