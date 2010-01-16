from twisted.web import resource

from xsbs.http.jsonapi import site as jsonSite, jsonMasterRequired, response

import sbserver
import json

class AdminSite(resource.Resource):
	pass

class SetMap(resource.Resource):
	def render_GET(self, request):
		request.setHeader('Content-Type', 'text/plain')
		try:
			map = request.args['map']
			mode = request.args['mode']
			mode_num = modeNumber(mode)
		except KeyError:
			return response('invalid_parameters', 'Valid map and mode name not specified')
		sbserver.setM
		return response('success')

def setup(jsonSite):
	'''Called by JSONAPI/api.py'''
	adminSite = AdminSite()
	adminSite.putChild('setmap', SetMap())
	jsonSite.putChild('admin', adminSite)

