from twisted.web import resource

from xsbs.http.jsonapi import JsonSite, JsonUserSite, response
from xsbs.users.privilege import isUserAdmin, isUserMaster

try:
	import json
except ImportError:
	import simplejson as json

class AccountSite(JsonUserSite):
	def render_user_JSON(self, request, user):
		return json.dumps({'user': {
			'id': user.id,
			'privileges': {
				'master': isUserMaster(user.id),
				'admin': isUserAdmin(user.id)
				}
			}})

class CreateAccountSite(JsonSite):
	def render_JSON(self, request):
		try:
			username = request.args['username'][0]
			password = request.args['password'][0]
		except (KeyError, IndexError):
			return response('invalid_parameters', 'Invalid username and or password')
		return resource('success')

def setup(jsonSite):
	accountSite = AccountSite()
	accountSite.putChild('create', CreateAccountSite())
	jsonSite.putChild('account', accountSite)

