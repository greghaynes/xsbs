from twisted.web import resource

from xsbs.http.jsonapi import site as jsonSite, jsonUserRequired, jsonAPI
from JSONAPI.admin import setup

from xsbs.players import all as allClients, player, playerCount, spectatorCount
from xsbs.users import userAuth
from xsbs.net import ipLongToString
from xsbs.ban import ban
from xsbs.game import currentMap, currentMode, modeName

import sbserver
import json

class AccountSite(resource.Resource):
	@jsonAPI
	@jsonUserRequired
	def render_GET(self, request, user):
		request.setHeader('Content-Type', 'text/plain')
		return json.dumps({'user': {
			'id': user.id
			}})
	@jsonAPI
	@jsonUserRequired
	def render_OPTIONS(self, request, user):
		request.setHeader('Content-Type', 'text/plain')
		return json.dumps({'user': {
			'id': user.id
			}})

class ScoreboardSite(resource.Resource):
	def render_GET(self, request):
		request.setHeader('Content-Type', 'text/plain')
		clients_response = []
		for p in allClients():
			clients_response.append({
				'cn': p.cn,
				'name': p.name(),
				'frags': p.frags(),
				'teamkills': p.teamkills(),
				'deaths': p.deaths(),
				})
			try:
				clients_response['team'] = p.team()
			except ValueError:
				clients_response['team'] = 'spectator'
		return json.dumps({'clients': clients_response})

class GameSite(resource.Resource):
	def render_GET(self, request):
		request.setHeader('Content-Type', 'text/plain')
		return json.dumps({
			'map': currentMap(),
			'mode': modeName(currentMode())
			})

class ServerSite(resource.Resource):
	def render_GET(self, request):
		request.setHeader('Content-Type', 'text/plain')
		return json.dumps({
			'num_clients': sbserver.numClients()
			})

jsonSite.putChild('account', AccountSite())
jsonSite.putChild('scoreboard', ScoreboardSite())
jsonSite.putChild('game', GameSite())
jsonSite.putChild('server', ServerSite())
setup(jsonSite)

