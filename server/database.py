import pickle
from math import pi
from StringIO import StringIO
from PIL import Image
import numpy as np
import base64

class Database():

  def __init__(self):
    self.subpours = dict()
    self.pours = dict()
    self.curr_subpour = 1
    self.curr_pour = 1

  def next_pour(self):
    self.curr_pour = self.curr_pour + 1
    return self.curr_pour - 1

  def next_subpour(self):
    self.curr_subpour = self.curr_subpour + 1
    return self.curr_subpour - 1

class PourData():

  def __init__(self, name, weight=None, temp=None, subpours=None):
    self.name = name
    self.weight = int(weight) if not weight in [None, ''] else 10
    self.temp = int(temp) if not temp in [None, ''] else 198
    self.subpours = subpours if not subpours == None else []

  def update(self, name, subpours, temperature, weight):
    self.name = name
    self.subpours = subpours
    self.temp = temperature
    self.weight = weight

class SubpourData():
  def __init__(self, name, duration=None, radius=None, r0=None, nrots=None, water=None, direction=None):
    self.name = name
    self.duration = int(duration) if not duration in ['', None] else 1
    self.r0 = float(r0) if not r0 in ['', None] else 0.0
    self.radius = float(radius) if not radius in ['', None] else 1.0
    self.nrots = int(nrots) if not nrots in ['',None] else 1
    self.water = float(water) if not water in ['', None] else 1.0
    self.direction = int(direction) if not direction in ['', None] else 1
    self.angle_rate = (2.0 * pi * self.nrots) / self.duration
    self.radius_rate = 1.0 / self.duration
  def draw(self):
    times = np.linspace(0, self.duration, 1024 * 8)
    angles = self.o0 + times * self.angle_rate
    radii = times * self.radius_rate
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
    return 'data:image/png;base64,' + outbuf.getvalue()
  def update(self, name, duration, radius, r0, nrots, water):
    self.name = name
    self.duration = int(duration) if not duration == '' else 1
    self.radius = float(radius) if not radius == '' else 1
    self.r0 = float(r0) if not r0 == '' else 0
    self.nrots = int(nrots) if not nrots == '' else 1
    self.water = water


