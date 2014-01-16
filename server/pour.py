from math import pi
from StringIO import StringIO
import logging
import serial
from PIL import Image
import numpy as np
import base64

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
	def draw(self):
		times = np.linspace(0, self.time, 1024 * 8)
		angles = times * self.angle_rate
		radii = times * self.radius_rate
		#pylab.plot(radii * np.cos(angles), radii * np.sin(angles))
		#axes = pylab.axes()
		#axes.get_xaxis().set_ticklabels([])
		#axes.get_yaxis().set_ticklabels([])
		image = np.empty((200, 200), np.uint8)
		image[:] = 255
		xs = np.rint(radii * np.cos(angles) * 99 + 100).astype(int)
		ys = np.rint(radii * np.sin(angles) * 99 + 100).astype(int)
		image[ys, xs] = 0
		image = Image.fromstring('L', (200,200), image.tostring())
		buf = StringIO()
		image.save(buf, format='PNG')
		outbuf = StringIO()
		buf.seek(0)
		base64.encode(buf, outbuf)
		return outbuf.getvalue()

def serialize(pours):
	buf = StringIO()
	for pour in pours:
		buf.write('theta_intital=0.0 theta_rate=' + str(pour.angle_rate))
		buf.write(' radius_initial=0.0 radius_rate=' + str(pour.radius_rate))
		buf.write(' time=' + str(pour.time) + ' pump=1.0\n')
		buf.write('theta_initial=0.0 theta_rate=0.0')
		buf.write(' radius_initial=1.0 radius_rate=' + str(-1.0 / pour.time_after))
		buf.write(' time=' + str(pour.time_after) + ' pump=0.0\n')
	return 'data:image/png;base64,' + buf.getvalue()

def send_pour(pours):
	if ser is None:
		logging.warn('No serial port')
		return False
	else:
		ser.write(serialize(pours))
		return True
