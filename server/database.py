import pickle

class Database(Base):
  
  subpours = dict()
  pours = dict()

  def __init__(self, fname):
    pass

  def save(self):
    pass
  def create

class PourData(Base):

  def __init__(self, subpours=None):
    pass

  def update(self, subpours):

from math import pi
from StringIO import StringIO
from PIL import Image
import numpy as np
import base64
class SubpourData(Base):
  def __init__(self, name, duration, radius, r0, o0, nrots, post_center):
    self.name = name
    self.duration = duration
    self.radius = radius
    self.r0 = r0
    self.o0 = o0
    self.nrots = nrots
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
  def update(self, name, duration, radius, r0, o0, nrots):
    pass


