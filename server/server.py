import cherrypy
import pickle
import database as db
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
  tmpl = lookup.get_template('pours.html')

  def table(self):
    pass

  def GET(self, n=None):
    if n==None:
      return self.tmpl.render() 
    else: 
      return n
      #pour = database.pours[n]

  def POST(self, **args):
    n = database.next_pour()
    return str(args)
    '''
    database.pours[n] = db.PourData(**args)
    save_data()
    '''
  def PUT(self, n, **args):
    database.pours[n].update(**args)
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
    tmpl = lookup.get_template('subpours.html')
    args = dict()
    args['n'] = n
    if n==None:
      args['form_method'] = 'POST' 
    else: 
      args['form_method'] = 'PUT'
    return tmpl.render(**args) 

  def POST(self, **args):
    global database
    args['water'] = 'water' in args
    args['post_center'] = 'post_center' in args
    n = database.next_subpour()
    database.subpours[n] = db.SubpourData(**args)
    save_data()
    f = open(datafilename)
    db_ = pickle.load(open(datafilename, 'r'))
    return 'sd' #+ str(database.subpours[n].name)
#raise cherrypy.HTTPRedirect('/subpours/' + str(n))

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
cherrypy.tree.mount(Pour().table, '/pours/table')
cherrypy.tree.mount(Subpour(), '/subpours',
{'/' : {'request.dispatch' : cherrypy.dispatch.MethodDispatcher()}})
cherrypy.tree.mount(Subpour().table, '/subpours/table')
server = Server()
cherrypy.quickstart(server, config=conf)
