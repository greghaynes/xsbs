from twisted.web import resource

from xsbs.http.jsonapi import site as jsonSite, jsonMasterRequired, response

from xsbs.game import modeNumber

import sbserver
import json

class AdminSite(resource.Resource):
	pass

class SetMap(resource.Resource):
	@jsonMasterRequired
	def render_GET(self, request):
		request.setHeader('Content-Type', 'text/plain')
		try:
			map = request.args['map'][0]
			mode = request.args['mode'][0]
			mode_num = modeNumber(mode)
		except (KeyError, ValueError):
			return response('invalid_parameters', 'Valid map and mode name not specified')
		sbserver.setMap(map, mode_num)
		return response('success')

def setup(jsonSite):
	'''Called by JSONAPI/api.py'''
	adminSite = AdminSite()
	adminSite.putChild('setmap', SetMap())
	jsonSite.putChild('admin', adminSite)

