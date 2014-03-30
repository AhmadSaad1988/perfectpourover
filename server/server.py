import cherrypy
import pickle
import database as db
from pour_serial_class_2 import pour_serial
from mako.template import Template
from mako.lookup import TemplateLookup
import os, os.path
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))

lookup = TemplateLookup(directories=['html'])

datafilename = 'data.pkl'
#ser = {}
pour_serial_obj = pour_serial()

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
    tmpl = lookup.get_template('pours.html')
    args = dict(subpour_names=self.get_subpour_names(), n=n, pours=database.pours)
    return tmpl.render(**args)

  def POST(self, **args):
    tmpl = lookup.get_template('pours.html')
    n = str(database.next_pour())
    subpours = args['subpours'].split(", ")
    if not args['name'] or len(subpours) == 0:
      return self.GET()
    database.pours[n] = db.PourData(name=args['name'], subpours=subpours)
    save_data()
    return tmpl.render(subpour_names=self.get_subpour_names(), n=n, pours=database.pours)

  def PUT(self, n, **args):
    subpours = args['subpours'].split(", ")
    if not args['name'] or len(subpours) == 0:
      return self.GET()
    database.pours[n].update(subpours=subpours, name=args['name'])
    save_data()

  def DELETE(self, n):
    del database.pours[n]

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
    if pour_serial_obj.ser is None:
      return "no arduino connected"
    elif pour_serial_obj.temperature is None:
      return "no response from arduino"
    else:
      resp = "water temp %.02f&deg;F" % pour_serial_obj.temperature
      if pour_serial_obj.pour_time is not None:
        resp += ", pouring for %.02f seconds" % pour_serial_obj.pour_time
      return resp

class RunPour:
  exposed = True
  def GET(self, n):
    send_pour([database.subpours[s] for s in database.pours[n].subpours])

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
cherrypy.tree.mount(RunPour(), '/run',
{'/' : {'request.dispatch' : cherrypy.dispatch.MethodDispatcher()}})
server = Server()
cherrypy.quickstart(server, config=conf)
