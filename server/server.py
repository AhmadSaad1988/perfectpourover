import cherrypy

class Server(object):

    @cherrypy.expose()
    def index(self):
        return 'noodles'

cherrypy.config.update({'server.socket_host': '127.0.0.1', 
                         'server.socket_port': 9999, 
                        }) 
cherrypy.quickstart(Server())
