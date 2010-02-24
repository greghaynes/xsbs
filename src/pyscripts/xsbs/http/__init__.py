from twisted.web import server, resource
from twisted.internet import reactor

from xsbs.settings import PluginConfig
from xsbs.events import eventHandler

config = PluginConfig('httpserver')
port = config.getOption('Config', 'port', '8081')
enable = config.getOption('Config', 'enable', 'yes') == 'yes'
port = int(port)
del config

class RootSite(resource.Resource):
		pass

class HttpServer(object):
	def __init__(self, address, port):
		self.address = address
		self.port = port
		self.root_site = RootSite()
		self.server_site = server.Site(self.root_site)
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

