import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))

lookup = TemplateLookup(directories=['html'])

class Server(object):

    @cherrypy.expose()
    def index(self):
        tmpl = lookup.get_template('base.html')
        return tmpl.render()

cherrypy.config.update({'server.socket_host': '127.0.0.1', 
                         'server.socket_port': 9999, 
                        }) 
conf = {'/dist': {'tools.staticdir.on': True, 'tools.staticdir.dir': os.path.join(current_dir, 'dist')}}
cherrypy.quickstart(Server(), '/', config=conf)
