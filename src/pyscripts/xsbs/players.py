from xsbs.events import registerServerEventHandler, triggerServerEvent
from xsbs.timers import addTimer
import sbserver
import logging

class Player:
	def __init__(self, cn):
		self.cn = cn
		self.gamevars = {}
	def newGame(self):
		self.gamevars.clear()
	def sessionId(self):
		return sbserver.playerSessionId(self.cn)
	def name(self):
		return sbserver.playerName(self.cn)
	def ipLong(self):
		return sbserver.playerIpLong(self.cn)
	def privilege(self):
		return sbserver.playerPrivilege(self.cn)
	def frags(self):
		return sbserver.playerFrags(self.cn)
	def teamkills(self):
		return sbserver.playerTeamkills(self.cn)
	def deaths(self):
		return sbserver.playerDeaths(self.cn)
	def ping(self):
		return sbserver.playerPing(self.cn)
	def team(self):
		return sbserver.playerTeam(self.cn)
	def isSpectator(self):
		return sbserver.playerIsSpectator(self.cn)
	def message(self, msg):
		sbserver.playerMessage(self.cn, msg)
	def kick(self):
		sbserver.playerKick(self.cn)
	def spectate(self):
		sbserver.spectate(self.cn)
	def unspectate(self):
		sbserver.unspectate(self.cn)
	def setTeam(self, team):
		sbserver.setTeam(self.cn, team)

players = {}

def onMapChanged(mapname, mapmode):
	for player in players.values():
		player.newGame();

def all():
	return players.values()

def player(cn):
	try:
		return players[cn]
	except KeyError:
		raise ValueError('Player does not exist')

def playerDisconnect(cn):
	try:
		del players[cn]
	except KeyError:
		logging.error('Player disconnected but does not have player class instance!')

def playerConnect(cn):
	try:
		del players[cn]
	except KeyError:
		pass
	players[cn] = Player(cn)
	addTimer(1000, triggerServerEvent, ('player_connect_delayed', (cn,)))

def reload():
	for cn in sbserver.clients():
		playerConnect(cn)

registerServerEventHandler('player_connect_pre', playerConnect)
registerServerEventHandler('player_disconnect_post', playerDisconnect)
registerServerEventHandler('restart_complete', reload)
registerServerEventHandler('map_changed', onMapChanged)

