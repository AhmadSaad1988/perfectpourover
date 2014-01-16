import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))

lookup = TemplateLookup(directories=['html'])
'''
datafilename = 'data.pkl'
datafile = open(datafilename, 'rwb')
database = pickle.load(datafile)
'''
def save_data():
  pickle.dump(datafile, database)

class Server(object):

  @cherrypy.expose()
  def index(self):
    tmpl = lookup.get_template('header.html')
    return tmpl.render()


class Pour(object):

  exposed = True

  @cherrypy.expose()
  def create(self):
    return 'create'

  @cherrypy.expose()
  def edit(self, n=None):
    return n

  def GET(self, n=None):
    if n==None:
      return "sup"
    else: 
      return n
      #pour = database.pours[n]

  def POST(self, **args):
    n = database.next_pour()
    database.pours[n] = PourData(**args)
    save_data()

  def PUT(self, n, **args):
    database.pours[n].update(**args)
    save_data()

  def DELETE(self, n):
    del database.pours[n] 

class Subpour(object):

  exposed = True

  @cherrypy.expose()
  def create(self):
    return 'create'

  @cherrypy.expose()
  def edit(self, n=None):
    return n
  
  def GET(self, n=None):
    if n==None:
      return "sup"
    else:
#subpour = database.subpours[n]
      return n     

  def POST(self, **args):
    n = database.next_subpour()
    database.subpours[n] = SubpourData(**args)
    save_data();

  def PUT(self, n, **args):
    database.subpours[n].update(**args)
    save_data()

  def DELETE(self, n):
    del database.subpours[n]

cherrypy.config.update({'server.socket_host': '127.0.0.1', 
             'server.socket_port': 9999, 
            }) 
conf = {'/css': {'tools.staticdir.on': True, 'tools.staticdir.dir': os.path.join(current_dir, 'css')}}

cherrypy.tree.mount(Pour(), '/pours',
{'/' : {'request.dispatch' : cherrypy.dispatch.MethodDispatcher()}})
cherrypy.tree.mount(Pour().create, '/pours/create')
cherrypy.tree.mount(Pour().edit, '/pours/edit')
cherrypy.tree.mount(Subpour(), '/subpours',
{'/' : {'request.dispatch' : cherrypy.dispatch.MethodDispatcher()}})
cherrypy.tree.mount(Subpour().create, '/subpours/create')
cherrypy.tree.mount(Subpour().edit, '/subpours/edit')
server = Server()
cherrypy.quickstart(server, config=conf)
