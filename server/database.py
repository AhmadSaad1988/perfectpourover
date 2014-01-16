import pickle

class Database(Base):
  
  subpours = dict()
  pours = dict()

  def __init__(self, fname):
    pass

  def save(self):
    pass
  def create

class Subpour(Base):
  
  def __init__(self, name, duration, radius, r0, o0, nrots):
    pass

  def update(self, name, duration, radius, r0, o0, nrots):
    pass


class Pour(Base):

  def __init__(self, subpours=None):
    pass

  def update(self, subpours):


