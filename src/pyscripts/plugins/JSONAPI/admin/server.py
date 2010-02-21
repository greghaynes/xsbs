from xsbs.http.jsonapi import JsonAtLeastMasterSite, response
from xsbs.game import setMap, modeNumber

class ServerSite(JsonAtLeastMasterSite):
	pass

class SetMapSite(JsonAtLeastMasterSite):
	def render_master_JSON(self, request, user):
		try:
			map = request.args['map'][0]
			mode = request.args['mode'][0]
			mode_num = modeNumber(mode)
		except (KeyError, ValueError):
			return response('invalid_parameters', 'Valid map and mode name not specified')
		setMap(map, mode_num)
		return response('success')

def setup(adminSite):
	serverSite = ServerSite()
	serverSite.putChild('setmap', SetMapSite())
	adminSite.putChild('server', serverSite)

