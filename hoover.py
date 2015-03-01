#!/usr/bin/python

#
# sudo pip install -U git+https://github.com/relayr/python-sdk
#

from relayr import Client
from relayr.dataconnection import MqttStream
from kryptoncon import KryptonCon
from decimal import *
import time
import json
import signal
import sys
import random

gyro="a2e4d803-82d2-4504-add2-8e99111d9178"

""" CONST """
ACC_THRES = 0.04    # at least one sensor (x,y,z) value need to be more different then this
DETECT_START_TIME = 3
DETECT_TIME = 5     # seconds
TIMEOUT = 60        # If the sensor doesn't send any data

IDLE=0              # when the hoover is still
TIME_TO_START=1     # the hoover moves but not longer DETECT_TIME
HOOVERING=2         # the hoover is running

TOK="Pm8az.iBVc6DBdHI7iKI9KDFu-VdKW4_"
GYROSCOPE_ID = 'a2e4d803-82d2-4504-add2-8e99111d9178'
SERVER = "http://192.168.178.115"
PORT = 3000

""" GLOBAL """
last_values = [0,0,0]
last_working = 0
start_time = 0
state = IDLE
stream = ""
con = ""


def get_diff(o, n):
    r = [];
    for i in range(0,3):
	r.append(o[i] - n[i])
    return r;

def is_working(o,n):
    diff = get_diff(o,n)
    for i in range(0,3):
	if (diff[i] >= ACC_THRES):
	    return True
    return False

def on_start_hoovering():
    con.start_msg();
    print "START HOOVERING!"

def on_finished_hoovering():
    con.end_msg();
    print "HOOOOOVERING Finished!!"

def validate_values(v):
    global last_values
    global state
    global last_working
    global start_time

    if (is_working(last_values, v)):
	last_working = time.time();

	if (state == IDLE):
	    start_time = last_working
	    state = TIME_TO_START
	elif (state == TIME_TO_START):
	    if (time.time() - start_time > DETECT_START_TIME):
		state = HOOVERING
		on_start_hoovering()
    else: 
	if (state != IDLE and time.time() - last_working > DETECT_TIME):
	    if (state == HOOVERING):
		on_finished_hoovering()
	    state = IDLE
    last_values = v


def mqtt_callback(topic, payload):
    j = json.loads(payload);
    for r in j['readings']:
	if (r['meaning'] == 'acceleration'):
	    validate_values(r['value'].values())


def on_signal(a, b):
    print "Bye Bye!"
    stream.stop();
    sys.exit(1);


if __name__ == "__main__":

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)
    random.seed()

    c = Client(token=TOK)
    con = KryptonCon(GYROSCOPE_ID, SERVER, PORT);
    dev = c.get_device(id=GYROSCOPE_ID)
    stream = MqttStream(mqtt_callback, [dev])
    stream.start()
    while True:
	time.sleep(10);
        print("Hoover-Daemon is (still) running :-) listening on sensor: '%s'  (%s)..." % (dev.get_info().name, dev.get_info().id))
	if (state != IDLE and time.time() - last_working > TIMEOUT):
	    print "Timeout occoured!!"
	    if (state == HOOVERING):
		on_finished_hoovering();

    stream.stop();

