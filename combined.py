import firebase_admin
import google.cloud
from firebase_admin import credentials, firestore

import time
import sys
import RPi.GPIO as GPIO
from hx711 import HX711

referenceUnit = 424
PIN_DOUT = 40
PIN_SCK = 38

PIN_TRIGGER = 7
PIN_ECHO = 11

DISTANCE_EMPTY = 3.31
DISTNACE_FULL = 32.98

def cleanAndExit():
    GPIO.cleanup()
    sys.exit()

def getDistance():
	GPIO.output(PIN_TRIGGER, GPIO.LOW)
	#      "Waiting for sensor to settle"
	time.sleep(2)
	#      "Calculating distance"
	GPIO.output(PIN_TRIGGER, GPIO.HIGH)

	time.sleep(0.00001)

	GPIO.output(PIN_TRIGGER, GPIO.LOW)

	while GPIO.input(PIN_ECHO)==0:
	    pulse_start_time = time.time()
	while GPIO.input(PIN_ECHO)==1:
	    pulse_end_time = time.time()

	pulse_duration = pulse_end_time - pulse_start_time
	distance = round(pulse_duration * 17150, 2)
	return max(0, distance)

#3.31, 32.98
def distanceToFullness( distance, distance_empty, distance_full ):
	data = float(distance)
	afteroffset = data - distance_empty
	afteroffset = min(distance_full, max(0, afteroffset))
	return round(abs((100 * ( afteroffset / distance_full )) - 100), 1)

#set up firebase
cred = credentials.Certificate("./smart-bin-77a5a-firebase-adminsdk-vlnzr-91e9d40740.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

# set up ultrasonic sensor
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)

# set up scale
hx = HX711(PIN_DOUT, PIN_SCK)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(referenceUnit)

# tare scale
hx.reset()
hx.tare()

while True:
    try:
        weight = max(0, int(hx.get_weight(5)))
        fullness_percentage = distanceToFullness(getDistance(), DISTANCE_EMPTY, DISTNACE_FULL)
        print(weight)
        print(fullness_percentage)

        db.collection('log').document().set({
			'weight': weight,
			'unit': u'g',
			'fullness': u''+str(fullness_percentage)+'%',
			'timestamp': firestore.SERVER_TIMESTAMP	
		})

        hx.power_down()
        hx.power_up()
        time.sleep(5)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()

