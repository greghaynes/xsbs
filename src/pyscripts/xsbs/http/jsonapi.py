from twisted.web import resource

from xsbs.http import server as httpServer
from xsbs.users import userAuth
from xsbs.users.privilege import isUserAtLeastMaster, isUserMaster, isUserAdmin

try:
	import json
except ImportError:
	import simplejson as json

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
	'not_logged_in': {
		'error': 'NOT_LOGGED_IN'
		},
	'insufficient_permissions': {
		'error': 'INSUFFICIENT_PERMISSIONS'
		},
	'success': {
		'result': 'SUCCESS'
		},
	'no_session': {
		'error': 'NO_SESSION'
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
		
		# Grab the session if it exists
		try:
			sesskey = request.args['sessionkey'][0]
		except KeyError:
			pass
		else:
			try:
				request.session = httpServer.sessionManager.sessions[sesskey]
			except KeyError:
				pass
		
		return self.render_JSON(request)
	def render_OPTIONS(self, request):
		setJsonHeaders(request)
		return None
	def render_JSON(self, request):
		return ''

class JsonSessionSite(resource.Resource):
	def render_JSON(self, request):
		try:
			session = request.session
		except AttributeError:
			return response('no_session', 'No active session')
		else:
			return self.render_session_JSON(request, session)

class JsonUserSite(JsonSessionSite):
	def render_session_JSON(self, request, session):
		try:
			user_id = session['user_id']
		except KeyError:
			return response('not_logged_in', 'Not currently logged in')
		return self.render_user_JSON(request, user_id)

class JsonAtLeastMasterSite(JsonUserSite):
	def render_user_JSON(self, request, user_id):
		if not isUserAtLeastMaster(user_id):
			return response('insufficient_permissions', 'User does not have master permissions')
		return self.render_master_JSON(request, user)		

class JsonMasterSite(JsonUserSite):
	def render_user_JSON(self, request, user_id):
		if not isUserMaster(user_id):
			return response('insufficient_permissions', 'User does not have master permissions')
		return self.render_master_JSON(request, user)		

class JsonAdminSite(JsonUserSite):
	def render_user_JSON(self, request, user_id):
		if not isUserAdmin(user_id):
			return response('insufficient_permissions', 'User does not have admin permissions')
		return self.render_admin_JSON(request, user)		

site = JsonSite()
httpServer.root_site.putChild('json', site)

