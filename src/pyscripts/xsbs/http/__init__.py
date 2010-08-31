from twisted.web import server, resource
from twisted.internet import reactor

from xsbs.settings import loadPluginConfig
from xsbs.events import eventHandler

from session import SessionManager

config = {
	'Main': {
			'port': '8081',
		}
	}

loadPluginConfig(config, 'http')
enable = True
port = int(config['Main']['port'])


class RootSite(resource.Resource):
		pass

class HttpServer(object):
	def __init__(self, address, port):
		self.address = address
		self.port = port
		self.root_site = RootSite()
		self.server_site = server.Site(self.root_site)
		self.session_manager = SessionManager()
	def start(self):
		self.connection = reactor.listenTCP(port, self.server_site)
	def stop(self):
		self.connection.stopListening()

server = HttpServer('', port)
if enable:
	server.start()

@eventHandler('reload')
def onReload():
	server.stop()
	server.start()

