from twisted.web import resource

from xsbs.http.jsonapi import JsonSite, JsonUserSite, site as jsonSite
from plugins.JSONAPI.admin import setup as setupAdmin
from plugins.JSONAPI.accounts import setup as setupAccounts
from plugins.JSONAPI.sessions import setup as setupSessions
from plugins.JSONAPI.user import setup as setupUser

from xsbs.players import all as allClients, player, playerCount, spectatorCount
from xsbs.users import userAuth
from xsbs.net import ipLongToString
from xsbs.ban import ban
from xsbs.game import currentMap, currentMode, modeName
from xsbs.users.privilege import isUserMaster, isUserAdmin

import sbserver

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

class ScoreboardSite(JsonSite):
	def render_JSON(self, request):
		clients_response = []
		for p in allClients():
			client = {
				'cn': p.cn,
				'name': p.name(),
				'frags': p.frags(),
				'teamkills': p.teamkills(),
				'deaths': p.deaths(),
				'privilege': p.privilege(),
				}
			try:
				client['team'] = p.team()
			except ValueError:
				client['team'] = 'spectator'
			try:
				client['is_verified'] = p.user != None
			except AttributeError:
				client['is_verified'] = False
			clients_response.append(client)
		return json.dumps({
			'clients': clients_response,
			'map': currentMap(),
			'mode': modeName(currentMode())
			})

class GameSite(JsonSite):
	def render_JSON(self, request):
		return json.dumps({
			'map': currentMap(),
			'mode': modeName(currentMode())
			})

class ServerSite(JsonSite):
	def render_JSON(self, request):
		return json.dumps({
			'num_clients': sbserver.numClients()
			})

def setup():
	jsonSite.putChild('scoreboard', ScoreboardSite())
	jsonSite.putChild('game', GameSite())
	jsonSite.putChild('server', ServerSite())
	setupAdmin(jsonSite)
	setupAccounts(jsonSite)
	setupSessions(jsonSite)
	setupUser(jsonSite)

setup()

