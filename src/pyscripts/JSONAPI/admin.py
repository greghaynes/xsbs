from twisted.web import resource

from xsbs.http.jsonapi import site as jsonSite, JsonAtLeastMasterSite, response

from xsbs.players import player
from xsbs.game import modeNumber

import sbserver
import json

class AdminSite(resource.Resource):
	pass

class SetMap(JsonAtLeastMasterSite):
	def render_master_JSON(self, request, user):
		try:
			map = request.args['map'][0]
			mode = request.args['mode'][0]
			mode_num = modeNumber(mode)
		except (KeyError, ValueError):
			return response('invalid_parameters', 'Valid map and mode name not specified')
		sbserver.setMap(map, mode_num)
		return response('success')

class KickSite(JsonAtLeastMasterSite):
	def render_master_JSON(self, request, user):
		try:
			player(int(request.args['cn'][0])).kick()
		except (ValueError, TypeError, KeyError):
			return response('invalid_parameters', 'No valid cn specified')
		return response('success')

def setup(jsonSite):
	'''Called by JSONAPI/api.py'''
	adminSite = AdminSite()
	adminSite.putChild('setmap', SetMap())
	adminSite.putChild('kick', KickSite())
	jsonSite.putChild('admin', adminSite)

