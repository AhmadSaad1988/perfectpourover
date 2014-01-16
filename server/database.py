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

class Subpour(Base):
  
  def __init__(self, name, duration, radius, r0, o0, nrots):
    pass

  def update(self, name, duration, radius, r0, o0, nrots):
    pass


class Pour(Base):

  def __init__(self, name, subpours=None):
    pass

  def update(self, subpours):
    pass


