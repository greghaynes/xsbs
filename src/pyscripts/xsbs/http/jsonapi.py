from twisted.web import resource

from xsbs.http import site as rootSite
from xsbs.users import userAuth
from xsbs.users.privilege import isUserAtLeastMaster

import json

class JsonSite(resource.Resource):
	pass

site = JsonSite()
rootSite.putChild('json', site)
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
		args[0].setHeader('Content-Type', 'application/json')
		args[0].setHeader('Access-Control-Allow-Origin', '*')
		args[0].setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
		args[0].setHeader('Access-Control-Allow-Headers', 'X-PINGOTHER, X-Requested-With, Accept')
		args[0].setHeader('Access-Control-Max-Age', '1728000')
		return self.f(*args, **kwargs)

class jsonUserRequired(object):
	def __init__(self, f):
		self.f = f
	def __call__(self, *args, **kwargs):
		args[0].setHeader('Content-Type', 'text/plain')
		try:
			username = args[0].args['username'][0]
			password = args[0].args['password'][0]
		except KeyError:
			return response('invalid_login', 'Missing username or password')
		user = userAuth(username, password)
		if not user:
			return response('invalid_login', 'No user found with matching username and password')
		return self.f(self, *(args + (user,)), **kwargs)

class jsonMasterRequired(object):
	def __init__(self, f):
		self.f = f
	def __call__(self, *args, **kwargs):
		args[0].setHeader('Content-Type', 'text/plain')
		try:
			username = args[0].args['username'][0]
			password = args[0].args['password'][0]
		except KeyError:
			return responses['invalid_login']
		user = userAuth(username, password)
		if not user:
			return responses['invalid_login']
		if isUserAtLeastMaster(user.id):
			return self.f(self, *(args + (user,)), **kwargs)
		else:
			return response('insufficient_permissions', 'User does not have master permissions')

