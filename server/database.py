import pickle

class Database(Base):
  
  subpours = dict()
  pours = dict()

  def __init__(self, fname):
    self.next_subpour = 1
    self.next_pour = 1
    pass

  def next_pour(self):
    self.next_pour = self.next_pour + 1
    return self.next_pour - 1

  def next_subpour(self):
    self.next_pour = self.next_subpour + 1
    return self.next_subpour - 1

class PourData(Base):

  def __init__(self, name, subpours=None):
    pass

  def update(self, subpours):
    pass

from math import pi
from StringIO import StringIO
from PIL import Image
import numpy as np
import base64
class SubpourData(Base):
  def __init__(self, name, duration, radius, r0, o0, nrots, water, post_center):
    self.name = name
    self.duration = duration
    self.radius = radius
    self.r0 = r0
    self.o0 = o0
    self.nrots = nrots
    self.water = water
    self.post_center = post_center
    self.num_rotations = num_rotations
    self.time = time
    self.time_after = time_after
    self.angle_rate = (2.0 * pi * nrots) / duration
    self.radius_rate = 1.0 / duration
  def draw(self):
    times = np.linspace(0, self.time, 1024 * 8)
    angles = self.o0 + times * self.angle_rate
    radii = self.r0 + times * self.radius_rate
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
  def update(self, name, duration, radius, r0, o0, nrots, water, post_center):
    pass


