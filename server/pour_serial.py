from math import pi
from StringIO import StringIO
import logging
import serial
from PIL import Image
import numpy as np
import base64
import threading

try:
	ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0.1)
except OSError:
	ser = None

temperature = None
def status_thread():
  while True:
    resp = ""
    while True:
      byte = ser.read()
      if byte == "\n":
        break
      else:
        resp.append(byte)

def serialize(subpours):
	buf = StringIO()
	for pour in subpours:
		buf.write('theta_intital=0.0 theta_rate=' + str(pour.angle_rate))
		buf.write(' radius_initial=0.0 radius_rate=' + str(pour.radius_rate))
		buf.write(' time=' + str(pour.time) + ' pump=1.0\n')
		buf.write('theta_initial=0.0 theta_rate=0.0')
		buf.write(' radius_initial=1.0 radius_rate=' + str(-1.0 / pour.time_after))
		buf.write(' time=' + str(pour.time_after) + ' pump=0.0\n')
	return 'data:image/png;base64,' + buf.getvalue()

def send_pour(subpours):
	if ser is None:
		logging.warn('No serial port')
		return False
	else:
		ser.write(serialize(subpours))
		return True
