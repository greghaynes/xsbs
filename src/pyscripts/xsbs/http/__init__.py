from twisted.web import server, resource
from twisted.internet import reactor

class RootSite(resource.Resource):
		pass

site = RootSite()
server_site = server.Site(site)
reactor.listenTCP(8081, server_site)

