from math import pi
from StringIO import StringIO
import logging
import serial
from PIL import Image
import numpy as np
import base64
import threading
from time import sleep

try:
	ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0.1)
except OSError:
	ser = None

temperature = None
pour_time = None
def status_thread():
  while True:
    resp = ""
    temp = None
    time = None
    while True:
      byte = ser.read()
      if byte == "\n":
        break
      else:
        resp += byte
    if resp == "TEMP":
      temp = True
    elif resp == "TIME":
      time = True
    elif resp == "END POUR":
      pour_time = None
      temp = None
      time = None
    elif temp is True:
      temperature = float(resp)
      temp = None
      time = None
    elif time is True:
      pour_time = float(resp)
      temp = None
      time = None
    else:
      print "'" + resp + "'"
    sleep(1)
if ser is not None:
  status_thread_obj = threading.Thread(target=status_thread)
  status_thread_obj.start()

def serialize(subpours):
  buf = StringIO()
  for pour in subpours:
    buf.write('LINEAR\n')
    # theta initial and rate
    buf.write('0.0\n' + str(pour.angle_rate) + '\n')
    # radius initial and rate
    buf.write('0.0\n' + str(pour.radius_rate) + '\n')
    # radius scale (in)
    buf.write('2\n') # XXX
    # time and pump on or off
    buf.write(str(float(pour.duration)) + '\n' + ('1' if pour.water else '0') + '\n')
    # temperature (F)
    buf.write('200\n')
  buf.write('END\n')
  return buf.getvalue()

def send_pour(subpours):
	if ser is None:
		logging.warn('No serial port')
		return False
	else:
		ser.write(serialize(subpours))
		return True
