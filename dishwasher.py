#!/usr/bin/python

#
# sudo pip install -U git+https://github.com/relayr/python-sdk
#
import pdb
import json
import relayr 
import time
from relayr import Client
from relayr.dataconnection import MqttStream
from kryptoncon import KryptonCon
import time
from sys import stdin

MIN_WORKING_TIME = 5
DO_DBG_RAPI_CONSOLE=False
DO_DBG_RAPI_LOGFILE=True

DO_DBG_STATE_CONSOLE=True
DO_DBG_STATE_LOGFILE=True

WG_TOKEN='Pm8az.iBVc6DBdHI7iKI9KDFu-VdKW4_'
DISHWASHER='f4ab513e-590d-494f-8586-2e06af2d186d'
DISHWASHER_KUECHE='637c568c-a48c-4282-ad5e-20993f6efb51'

def dbg_rapi(msg):
    if DO_DBG_RAPI_CONSOLE:
        print(msg)
    if DO_DBG_RAPI_LOGFILE:
        logfile = open("/tmp/dish_rapi.log", 'a')
        logfile.write("%s\n"%msg)
        logfile.close()

def dbg_state_machine(msg):
    if DO_DBG_STATE_CONSOLE:
        print(msg)
    if DO_DBG_STATE_LOGFILE:
        logfile = open("/tmp/dish_state.log", 'a')
        logfile.write("%s\n"%msg)
        logfile.close()

def dirty_trans_fn(state, sensor_val):
    machine = state.machine
    if (sensor_val == "active"):
            machine.set_state( machine.cleaning ) 

def cleaning_trans_fn(state, sensor_val):
    machine = state.machine
    if (sensor_val == "finished"):
        machine.kryptcon.start_msg()
        machine.set_state( machine.finished ) 

def finished_trans_fn(state, sensor_val):
    machine = state.machine
    if (sensor_val == "open" ):
        machine.set_state( machine.working_player ) 

def working_player_trans_fn(state, sensor_val):
    machine = state.machine

    if (sensor_val == "closed" ):
        now = int(time.time())
        if state.state_entered_since + MIN_WORKING_TIME < now:
            machine.kryptcon.end_msg()
            machine.set_state( machine.dirty ) 
        else:
            machine.set_state( machine.finished ) 


class State():
    def __init__( self, machine, name, trans_func ):
        self.machine = machine
        self.name = name
        self.trans_func = trans_func

    def reset_state(self):
        #dbg_state_machine("reset state %s"%self.name)
        self.state_entered_since = int(time.time())


class DishMachine():
    def __init__(self, kryptcon):
        self.kryptcon = kryptcon
        self.dirty          = State(self, 'dirty'            , dirty_trans_fn)
        self.cleaning       = State(self, 'cleaning'         , cleaning_trans_fn)
        self.finished       = State(self, 'finished'         , finished_trans_fn)
        self.working_player = State(self, 'working_player'   , working_player_trans_fn)
        self.set_state( self.dirty )

    def machine_step(self, sensor_val):
        self.current_state.trans_func( self.current_state, sensor_val )

    def set_state(self, state):
        state.reset_state()
        self.current_state = state
        dbg_state_machine("entering_state: %s"%state.name)


def distance_callback(topic, payload):
    dbg_rapi(payload)
    readings = json.loads(payload)["readings"]
    for element in readings:
        if element["meaning"] == 'proximity':
            distance = element['value'];
            print(distance)
            dish_machine.machine_step(distance)

def list_all_devices(relayr_usr):
    devs = relayr_usr.get_devices()
    for d in devs:
        info = d.get_info()
        print("dev '%s' (%s) " % (info.name, info.id))
    #pdb.set_trace()

def toggle_led_all_devices(relayr_usr):
    devs = relayr_usr.get_devices()
    for d in devs:
        d.switch_led_on(True)


if __name__ == "__main__":

    kryptcon = KryptonCon( DISHWASHER )
    dish_machine = DishMachine( kryptcon )

    while True:
        print("enter: active finished open closed")
        userinput = stdin.readline().strip()
        dish_machine.machine_step( userinput )

"""
    relayr_client = relayr.Client(token=WG_TOKEN)
    relayr_usr = relayr_client.get_user()
    # list_all_devices(relayr_usr)
    # toggle_led_all_devices(relayr_usr)
    dev = relayr_client.get_device(id=LIGHT)
    app = relayr_client.get_app()
    dbg_rapi(app)

    stream = MqttStream(distance_callback, [dev])
    stream.start()

    while True:
        print("Daemon is (still) running :-) listening on sensor: '%s'  (%s)..." % (dev.get_info().name, dev.get_info().id))
        time.sleep(600)

    stream.stop()
"""



