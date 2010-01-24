from xsbs.http.jsonapi import JsonAtLeastMasterSite, response
from xsbs.players import player

class ClientsSite(JsonAtLeastMasterSite):
	pass

class KickSite(JsonAtLeastMasterSite):
	def render_master_JSON(self, request, user):
		try:
			player(int(request.args['cn'][0])).kick()
		except (ValueError, TypeError, KeyError):
			return response('invalid_parameters', 'No valid cn specified')
		return response('success')

def setup(adminSite):
	clientsSite = ClientsSite()
	clientsSite.putChild('kick', KickSite())
	adminSite.putChild('clients', clientsSite)

