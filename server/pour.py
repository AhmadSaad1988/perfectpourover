from math import pi
from StringIO import StringIO
import logging
import serial

try:
	ser = serial.Serial('/dev/ttyACM0', 9600)
except OSError:
	ser = None

class Pour:
	def __init__(self, num_rotations, time, time_after):
		self.num_rotations = num_rotations
		self.time = time
		self.time_after = time_after
		self.angle_rate = (2.0 * pi * num_rotations) / time
		self.radius_rate = 1.0 / time

def serialize(pours):
	buf = StringIO()
	for pour in pours:
		buf.write('theta_intital=0.0 theta_rate=' + str(pour.angle_rate))
		buf.write(' radius_initial=0.0 radius_rate=' + str(pour.radius_rate))
		buf.write(' time=' + str(pour.time) + '\n')
		buf.write('theta_initial=0.0 theta_rate=0.0')
		buf.write(' radius_initial=1.0 radius_rate=' + str(-1.0 / pour.time_after))
		buf.write(' time=' + str(pour.time_after) + '\n')
	return buf.getvalue()

def send_pour(pours):
	if ser is None:
		logging.warn('No serial port')
		return False
	else:
		ser.write(serialize(pours))
		return True
