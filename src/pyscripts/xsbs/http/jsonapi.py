from twisted.web import resource

from xsbs.http import server as httpServer
from xsbs.users import userAuth
from xsbs.users.privilege import isUserAtLeastMaster

import json

def setJsonHeaders(request):
	request.setHeader('Content-Type', 'application/json')
	request.setHeader('Access-Control-Allow-Origin', '*')
	request.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
	request.setHeader('Access-Control-Allow-Headers', 'X-PINGOTHER, X-Requested-With, Accept')
	request.setHeader('Access-Control-Max-Age', '1728000')

default_responses = {
	'invalid_parameters': {
		'error': 'INVALID_PARAMETERS'
		},
	'invalid_login': {
		'error': 'INVALID_LOGIN'
		},
	'insufficient_permissions': {
		'error': 'INSUFFICIENT_PERMISSIONS'
		},
	'success': {
		'result': 'SUCCESS'
		}
	}

def response(name, description=None, **kwargs):
	response = default_responses[name].copy()
	if description != None:
		response['description'] = description
	response.update(kwargs)
	return json.dumps(response)

class jsonAPI(object):
	def __init__(self, f):
		self.f = f
	def __call__(self, *args, **kwargs):
		setJsonHeaders(args[1])
		return self.f(*args, **kwargs)

class JsonSite(resource.Resource):
	def render_GET(self, request):
		setJsonHeaders(request)
		return self.render_JSON(request)
	def render_OPTIONS(self, request):
		setJsonHeaders(request)
		return None
	def render_JSON(self, request):
		return ''

class JsonUserSite(JsonSite):
	def render_JSON(self, request):
		try:
			username = request.args['username'][0]
			password = request.args['password'][0]
		except KeyError:
			return response('invalid_login', 'Missing username or password')
		user = userAuth(username, password)
		if not user:
			return response('invalid_login', 'No user found with matching username and password')
		return self.render_user_JSON(request, user)

class JsonAtLeastMasterSite(JsonUserSite):
	def render_user_JSON(self, request, user):
		if not isUserAtLeastMaster(user.id):
			return response('insufficient_permissions', 'User does not have master permissions')
		return self.render_master_JSON(request, user)		

class JsonMasterSite(JsonUserSite):
	def render_user_JSON(self, request, user):
		if not isUserMaster(user.id):
			return response('insufficient_permissions', 'User does not have master permissions')
		return self.render_master_JSON(request, user)		

site = JsonSite()
httpServer.root_site.putChild('json', site)

class jsonMasterRequired(object):
	def __init__(self, f):
		self.f = f
	def __call__(self, *args, **kwargs):
		args[0].setHeader('Content-Type', 'text/plain')
		try:
			username = args[1].args['username'][0]
			password = args[1].args['password'][0]
		except KeyError:
			return responses['invalid_login']
		user = userAuth(username, password)
		if not user:
			return responses['invalid_login']
		if isUserAtLeastMaster(user.id):
			return self.f(*(args + (user,)), **kwargs)
		else:
			return response('insufficient_permissions', 'User does not have master permissions')

