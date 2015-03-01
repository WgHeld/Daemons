#!/usr/bin/python

#
# sudo pip install -U git+https://github.com/relayr/python-sdk
#
import json
import relayr 
import time
from relayr import Client
from relayr.dataconnection import MqttStream
from kryptoncon import KryptonCon
import time

DO_DBG_RAPI_CONSOLE=False
DO_DBG_RAPI_LOGFILE=True

DO_DBG_STATE_CONSOLE=False
DO_DBG_STATE_LOGFILE=True

WG_TOKEN='Pm8az.iBVc6DBdHI7iKI9KDFu-VdKW4_'
LIGHT='103156b3-1a78-42c2-a4af-1512721ded3d'

EMPTY_THRLD =  100
HALF_THRLD  =  200
FULL_THRLD  = 1500
COND_TIME   = 5

def dbg_rapi(msg):
    if DO_DBG_RAPI_CONSOLE:
        print(msg)
    if DO_DBG_RAPI_LOGFILE:
        logfile = open("/tmp/rapi.log", 'a')
        logfile.write("%s\n"%msg)
        logfile.close()

def dbg_state_machine(msg):
    if DO_DBG_STATE_CONSOLE:
        print(msg)
    if DO_DBG_STATE_LOGFILE:
        logfile = open("/tmp/state.log", 'a')
        logfile.write("%s\n"%msg)
        logfile.close()

def empty_trans_fn(state, sensor_val):
    machine = state.machine
    if (sensor_val > HALF_THRLD):
        if state.condition_met_long_enouph():
            machine.set_state( machine.half_full ) 
    else:
        state.reset_state()

def half_full_trans_fn(state, sensor_val):
    machine = state.machine
    if (sensor_val > FULL_THRLD):
        if state.condition_met_long_enouph():
            kryptcon.start_msg()
            machine.set_state( machine.full ) 
    else:
        state.reset_state()

def full_trans_fn(state, sensor_val):
    machine = state.machine
    if (sensor_val < EMPTY_THRLD):
        if state.condition_met_long_enouph():
            kryptcon.end_msg()
            machine.set_state( machine.empty ) 
    else:
        state.reset_state()


class State():
    def __init__( self, machine, name, trans_func, condition_time=COND_TIME ):
        self.machine = machine
        self.name = name
        self.trans_func = trans_func
        self.condition_time = condition_time

    def condition_met_long_enouph(self):
        now = int(time.time())

        if self.cond_met_since == 0:
            self.cond_met_since = now
            
        waited_for = now - self.cond_met_since 
        if waited_for > self.condition_time:
            dbg_state_machine("thank you for your patience: %s"%self.name)
            return True

        dbg_state_machine("need more time %s (%d/%d)"%(self.name, waited_for, self.condition_time))
        return False

    def reset_state(self):
        dbg_state_machine("reset state %s"%self.name)
        self.cond_met_since = 0


class TrashMachine():
    def __init__(self, kryptcon):
        self.kryptcon = kryptcon
        self.empty         = State(self, 'empty'      , empty_trans_fn)
        self.half_full     = State(self, 'half_full'  , half_full_trans_fn)
        self.full          = State(self, 'full'       , full_trans_fn)
        self.set_state( self.empty )

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
            trash_machine.machine_step(distance)

def list_all_devices(relayr_usr):
    devs = relayr_usr.get_devices()
    for d in devs:
        info = d.get_info()
        print("dev '%s' (%s) " % (info.name, info.id))

def toggle_led_all_devices(relayr_usr):
    devs = relayr_usr.get_devices()
    for d in devs:
        d.switch_led_on(True)


if __name__ == "__main__":

    kryptcon = KryptonCon( LIGHT )

    trash_machine = TrashMachine( kryptcon )
    relayr_client = relayr.Client(token=WG_TOKEN)
    relayr_usr = relayr_client.get_user()
    #list_all_devices(relayr_usr)
    dev = relayr_client.get_device(id=LIGHT)
    app = relayr_client.get_app()
    dbg_rapi(app)

    stream = MqttStream(distance_callback, [dev])
    stream.start()

    while True:
        print("Daemon is (still) running :-) listening on sensor: '%s'  (%s)..." % (dev.get_info().name, dev.get_info().id))
        time.sleep(600)

    stream.stop()

    time.sleep(10);



