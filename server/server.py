import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))

lookup = TemplateLookup(directories=['html'])

datafilename = 'data.pkl'
datafile = open('datak.pkl', 'rwb')
database = pickle.load(datafile)

def save_data():
  pickle.dump(datafile, database)

class Server(object):

  @cherrypy.expose()
  def index(self):
    tmpl = lookup.get_template('header.html')
    return tmpl.render()


class Pour(object):
  
  def GET(self, id=None):
    pour = database.pours[id]
    pass

  def POST(self, name):
    database.
    save_data()
    pass

  def PUT(self, name, seq):
    pass

  def DELETE(self, id):
    pass

class Subpour(object):
  
  def GET(self, id=None):
    pass

  def POST(self, name, duration, radius, r0, o0, nrots, post_center):
    pass

  def PUT(self, name, duration, radius, r0, o0, nrots, post_center):
    pass

  def DELETE(self, id):
    pass

cherrypy.config.update({'server.socket_host': '127.0.0.1', 
             'server.socket_port': 9999, 
            }) 
conf = {'/css': {'tools.staticdir.on': True, 'tools.staticdir.dir': os.path.join(current_dir, 'css')}}
cherrypy.quickstart(Server(), config=conf)
