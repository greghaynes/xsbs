from twisted.web import resource

from xsbs.http import site as rootSite
from xsbs.users import userAuth
from xsbs.users.privilege import isUserAtLeastMaster

import json

class JsonSite(resource.Resource):
	pass

site = JsonSite()
rootSite.putChild('json', site)

class jsonUserRequired(object):
	def __init__(self, f):
		self.f = f
	def __call__(self, *args, **kwargs):
		args[0].setHeader('Content-Type', 'text/plain')
		try:
			username = args[0].args['username'][0]
			password = args[0].args['password'][0]
		except KeyError:
			return json.dumps({'error': 'INVALID_LOGIN'})
		user = userAuth(username, password)
		if not user:
			return json.dumps({'error': 'INVALID_LOGIN'})
		self.f(self, *(args + user), **kwargs)

class jsonMasterRequired(object):
	def __init__(self, f):
		self.f = f
	def __call__(self, *args, **kwargs):
		args[0].setHeader('Content-Type', 'text/plain')
		try:
			username = args[0].args['username'][0]
			password = args[0].args['password'][0]
		except KeyError:
			return json.dumps({'error': 'INVALID_LOGIN'})
		user = userAuth(username, password)
		if not user:
			return json.dumps({'error': 'INVALID_LOGIN'})
		if isUserAtLeastMaster(user.id):
			self.f(self, *(args + user), **kwargs)
		else:
			return json.dumps({'error': 'INSUFFICIENT_PERMISSIONS'})

class jsonResponse(object):
	def __init__(self, f):
		self.f = f
	def __call__(self, *args, **kwargs):
		args[0].setHeader('Content-Type', 'text/plain')
		self.f(*args, **kwargs)

