from twisted.web import resource

from xsbs.http.jsonapi import site as jsonSite, jsonUserRequired, jsonMasterRequired

from xsbs.players import all as allClients, player, playerCount, spectatorCount
from xsbs.users import userAuth
from xsbs.net import ipLongToString
from xsbs.ban import ban
import sbserver
import json

class AccountSite(resource.Resource):
	@jsonUserRequired
	def render_GET(self, request, user):
		request.setHeader('Content-Type', 'text/plain')
		return json.dumps({'user': {
			'id': user.id
			}})

jsonSite.putChild('account', AccountSite())

