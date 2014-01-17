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

  def __init__(self, name, weight, subpours=None):
    self.name = name
    self.subpours = subpours

  def update(self, name, subpours=None):
    self.name = name
    self.subpours = subpours

class SubpourData():
  def __init__(self, name, duration, radius, r0, nrots, water, direction):
    self.name = name
    self.duration = int(duration) if not duration == '' else 1
    self.radius = float(radius) if not radius == '' else 1
    self.nrots = int(nrots) if not nrots == '' else 1
    self.water = water
    self.post_center = post_center
    #self.time_after = time_after
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
    return outbuf.getvalue()
  def update(self, name, duration, radius, nrots, water, post_center):
    self.name = name
    self.duration = int(duration) if not duration == '' else 1
    self.radius = float(radius) if not radius == '' else 1
    self.nrots = int(nrots) if not nrots == '' else 1
    self.water = water
    self.post_center = post_center


