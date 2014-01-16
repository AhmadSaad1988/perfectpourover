import cherrypy
import pickle
import database as db
import pour_serial
from mako.template import Template
from mako.lookup import TemplateLookup
import os, os.path
current_dir = os.path.dirname(os.path.abspath(__file__))

lookup = TemplateLookup(directories=['html'])

datafilename = 'data.pkl'

try:
  database = pickle.load(open(datafilename, 'r'))
except IOError:
  database = db.Database()



def save_data():
  global database
  pickle.dump(database, open(datafilename, 'w'))
  dbase = pickle.load(open(datafilename, 'r'))

class Server(object):

  @cherrypy.expose()
  def index(self):
    tmpl = lookup.get_template('header.html')
    return tmpl.render()


class Pour(object):

  exposed = True

  def table(self):
    pass

  def get_subpour_names(self):
    return dict((num, database.subpours[num].name)
                      for num in database.subpours.keys())

  def GET(self, n=None):
    if n is not None:
      n = int(n)
    tmpl = lookup.get_template('pours.html')
    args = dict(subpour_names=self.get_subpour_names(), n=n, pours=database.pours)
    return tmpl.render(**args)

  def POST(self, **args):
    tmpl = lookup.get_template('pours.html')
    n = database.next_pour()
    subpours = map(int, args['subpours'].split(", "))
    if not args['name'] or len(subpours) == 0:
      return self.GET()
    database.pours[n] = db.PourData(name=args['name'], subpours=subpours)
    save_data()
    return tmpl.render(subpour_names=self.get_subpour_names(), n=n, pours=database.pours)

  def PUT(self, n, **args):
    n = int(n)
    subpours = map(int, args['subpours'].split(", "))
    if not args['name'] or len(subpours) == 0:
      return self.GET()
    print n, type(n)
    database.pours[n].update(subpours=subpours, name=args['name'])
    save_data()

  def DELETE(self, n):
    del database.pours[int(n)] 

class Subpour(object):

  exposed = True

  @cherrypy.expose()
  def table(self):
    tmpl = lookup.get_template('subpours_table.html')
    return tmpl.render(subpours=database.subpours)

   
  def GET(self, n=None):
    global database
    tmpl = lookup.get_template('subpours.html')
    args = dict()
    args['n'] = n
    args['subpours'] = database.subpours
    if n==None:
      args['form_method'] = 'POST' 
    else: 
      args['form_method'] = 'PUT'
    return tmpl.render(**args) 

  def POST(self, **args):
    global database
    args['water'] = 'water' in args
    args['post_center'] = 'post_center' in args
    n = str(database.next_subpour())
    database.subpours[n] = db.SubpourData(**args)
    save_data()
    f = open(datafilename)
    db_ = pickle.load(open(datafilename, 'r'))
    raise cherrypy.HTTPRedirect('/subpours/' + str(n))

  def PUT(self, n, **args):
    global database
    args['water'] = 'water' in args
    args['post_center'] = 'post_center' in args
    database.subpours[n].update(**args)
    save_data()
    raise cherrypy.HTTPRedirect('/subpours/' + str(n))

  def DELETE(self, n):
    global database
    del database.subpours[n]
    raise cherrypy.HTTPRedirect('/subpours/')

class status:
  exposed = True
  def GET(self):
    if pour_serial.temperature is None:
      return "no response from server"
    else:
      return "water temp %d&deg;F" % pour_serial.temperature

cherrypy.config.update({'server.socket_host': '127.0.0.1', 
             'server.socket_port': 9999, 
            }) 
conf = {'/css': {'tools.staticdir.on': True, 'tools.staticdir.dir': os.path.join(current_dir, 'css')},
        '/jquery-ui': {'tools.staticdir.on': True, 'tools.staticdir.dir': os.path.join(current_dir, 'jquery-ui')}}

cherrypy.tree.mount(Pour(), '/pours',
{'/' : {'request.dispatch' : cherrypy.dispatch.MethodDispatcher()}})
cherrypy.tree.mount(Pour().table, '/pours/table')
cherrypy.tree.mount(Subpour(), '/subpours',
{'/' : {'request.dispatch' : cherrypy.dispatch.MethodDispatcher()}})
cherrypy.tree.mount(Subpour().table, '/subpours/table')
cherrypy.tree.mount(status(), '/status',
{'/' : {'request.dispatch' : cherrypy.dispatch.MethodDispatcher()}})
server = Server()
cherrypy.quickstart(server, config=conf)
