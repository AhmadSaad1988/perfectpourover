from StringIO import StringIO
import logging
import serial
from PIL import Image
import numpy as np
import base64
import threading
import sys
from time import sleep

class pour_serial(object) :

  def status_thread(self):
    while True:
      if self.ser == None:
        continue
      resp = ''
      while True:
        byte = self.ser.read()
        import sys
        #sys.stderr.write(byte)
        if byte == "\n":
          sys.stderr.write(resp + "\n")
          break
        else:
          resp += byte
      if resp.rstrip() == "TEMP":
        self.temp = True
      elif resp.rstrip() == "TIME":
        self.time = True
      elif resp.rstrip() == "END POUR":
        self.pour_time = None
        self.temp = False
        self.time = False
      elif self.temp is True:
        self.temperature = float(resp.rstrip())
        self.temp = False
        self.time = False
      elif self.time is True:
        self.pour_time = float(resp.rstrip())
        self.temp = False
        self.time = False
      if self.temperature != None:
        print 'Self temperature %f' % self.temperature
      sleep(1)


  def serialize(subpours):
    buf = StringIO()
    for pour in subpours:
      buf.write('LINEAR\n')
      # theta initial and rate
      buf.write('0.0\n' + str(pour.angle_rate) + '\n')
      # radius initial and rate
      buf.write('0.0\n' + str(pour.radius_rate) + '\n')
      # radius scale (in)
      buf.write('2.0\n')
      # time and pump on or off
      buf.write(str(float(pour.duration)) + '\n1\n')
      # temperature (F)
      buf.write('67\n')
      buf.write('LINEAR\n')
      buf.write('0.0\n0.0\n')
      radius = pour.radius_rate * pour.duration
      buf.write(str(radius) + '\n' + str(-radius/2.0) + '\n')
      buf.write('2.0\n')
      buf.write('2.0\n1\n')
      buf.write('200\n')
    buf.write('END\n')
    return buf.getvalue()

  def send_pour(self,subpours):
  	if self.ser is None:
  		logging.warn('No serial port')
  		return False
  	else:
  		self.ser.write(serialize(subpours))
  		self.ser.flush()
  		return True
  def __init__(self):
    object.__init__(self)
    self.ser = None
    self.temp = False
    self.time = False
    self.temperature = None
    self.pour_time = None
    try:
      self.ser = serial.Serial('/dev/tty.usbmodem621', 9600)
    except OSError:
      print "Serial Error"
      self.ser = None
    status_thread_obj = None
    if self.ser is not None:
      status_thread_obj = threading.Thread(target=self.status_thread())
      status_thread_obj.start()
