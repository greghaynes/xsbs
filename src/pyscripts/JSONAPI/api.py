from twisted.web import resource

from xsbs.http.jsonapi import JsonSite, JsonUserSite, site as jsonSite
from JSONAPI.admin import setup as setupAdmin

from xsbs.players import all as allClients, player, playerCount, spectatorCount
from xsbs.users import userAuth
from xsbs.net import ipLongToString
from xsbs.ban import ban
from xsbs.game import currentMap, currentMode, modeName
from xsbs.users.privilege import isUserMaster, isUserAdmin

import sbserver
import json

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
				}
			try:
				client['team'] = p.team()
			except ValueError:
				client['team'] = 'spectator'
			clients_response.append(client)
		return json.dumps({'clients': clients_response})

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
	jsonSite.putChild('account', AccountSite())
	jsonSite.putChild('scoreboard', ScoreboardSite())
	jsonSite.putChild('game', GameSite())
	jsonSite.putChild('server', ServerSite())
	setupAdmin(jsonSite)

setup()

