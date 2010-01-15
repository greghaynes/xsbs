from twisted.web import server, resource
from twisted.internet import reactor

from xsbs.settings import PluginConfig

config = PluginConfig('httpserver')
port = config.getOption('Config', 'port', '8081')
port = int(port)
del config

class RootSite(resource.Resource):
		pass

site = RootSite()
server_site = server.Site(site)
reactor.listenTCP(port, server_site)

