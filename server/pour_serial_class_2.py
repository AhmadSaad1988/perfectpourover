from StringIO import StringIO
import logging
import serial
from PIL import Image
import numpy as np
import base64
import threading
from time import sleep
import sys

class pour_serial:

  def __init__(self):
    self.temperature = None
    self.pour_time = None
    self.ser = None
    self.foo = 42
    self.temp_flag = False
    self.time_flag = False

    try:
    	self.ser = serial.Serial('/dev/tty.usbmodem621', 9600, timeout=0.1)
    except OSError:
    	self.ser = None

    if self.ser is not None:
      status_thread_obj = threading.Thread(target=self.status_thread)
      status_thread_obj.start()

  def status_thread(self):
    while True:
      resp = ""

      # Read response
      while True:
        byte = self.ser.read()
        
        if byte == "\n":
          self.foo = self.foo + 1
          print resp
          break
        else:
          resp += byte

      # Handle Response 
      if resp.rstrip() == "TEMP":
        print "Found a TEMP"
        self.temp_flag = True
      elif resp.rstrip() == "TIME":
        self.time_flag = True
      elif resp.rstrip() == "END POUR":
        self.pour_time = None
        self.temp_flag = False
        self.time_flag = False
      elif self.temp_flag is True:
        print "Setting temp"
        self.temperature = float(resp.rstrip())
        self.temp_flag = False
        self.time_flag = False
      elif self.time_flag is True:
        self.pour_time = float(resp.rstrip())
        self.temp_flag = None
        self.time_flag = None

      # Wait for next response
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
      buf.write('200\n')
      buf.write('LINEAR\n')
      buf.write('0.0\n0.0\n')
      radius = pour.radius_rate * pour.duration
      buf.write(str(radius) + '\n' + str(-radius/2.0) + '\n')
      buf.write('2.0\n')
      buf.write('2.0\n1\n')
      buf.write('200\n')
    buf.write('END\n')
    return buf.getvalue()

  def send_pour(self, subpours):
  	if self.ser is None:
  		logging.warn('No serial port')
  		return False
  	else:
  		self.ser.write(serialize(subpours))
  		self.ser.flush()
  		return True
