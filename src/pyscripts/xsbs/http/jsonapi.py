from twisted.web import resource

from xsbs.http import site as rootSite

class JsonSite(resource.Resource):
	pass

site = JsonSite()
rootSite.putChild('json', site)

def putChild(name, resource):
	site.putChild(name, resource)

