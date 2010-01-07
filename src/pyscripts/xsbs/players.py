from xsbs.events import eventHandler, triggerServerEvent
from xsbs.timers import addTimer
from xsbs.net import ipLongToString
import sbserver
import logging

class Player:
	'''Represents a client on the server'''
	def __init__(self, cn):
		self.cn = cn
		self.gamevars = {}
	def newGame(self):
		'''Reset game variables'''
		self.gamevars.clear()
	def sessionId(self):
		'''Session ID of client'''
		return sbserver.playerSessionId(self.cn)
	def name(self):
		'''Name of client'''
		return sbserver.playerName(self.cn)
	def ipLong(self):
		'''Ip of client as long'''
		return sbserver.playerIpLong(self.cn)
	def ipString(self):
		'''Ip of client as decimal octet string'''
		return ipLongToString(self.ipLong())
	def privilege(self):
		'''Integer privilege of client'''
		return sbserver.playerPrivilege(self.cn)
	def frags(self):
		'''Frags by client in current game'''
		return sbserver.playerFrags(self.cn)
	def teamkills(self):
		'''Team kills by client in current game'''
		return sbserver.playerTeamkills(self.cn)
	def deaths(self):
		'''Deaths by client in current game'''
		return sbserver.playerDeaths(self.cn)
	def ping(self):
		'''Last reported ping of client'''
		return sbserver.playerPing(self.cn)
	def team(self):
		'''Name of team client belongs to'''
		return sbserver.playerTeam(self.cn)
	def isSpectator(self):
		'''Is client a spectator'''
		return sbserver.playerIsSpectator(self.cn)
	def message(self, msg):
		'''Send message to client'''
		sbserver.playerMessage(self.cn, msg)
	def kick(self):
		'''Disconnect client from server'''
		sbserver.playerKick(self.cn)
	def spectate(self):
		'''Make client spectator'''
		sbserver.spectate(self.cn)
	def unspectate(self):
		'''Make client not a spectator'''
		sbserver.unspectate(self.cn)
	def setTeam(self, team):
		'''Set team client belongs to'''
		sbserver.setTeam(self.cn, team)

players = {}

@eventHandler('map_changed')
def onMapChanged(mapname, mapmode):
	for player in players.values():
		player.newGame();

def all():
	'''Get list of all clients'''
	return players.values()

def cnsToPlayers(cns):
	'''Turn list of cn's into list of Player's'''
	ps = []
	for cn in cns:
		ps.append(player(cn))
	return ps

def clientCount():
	'''Number of clients connected to server'''
	return len(sbserver.clients())

def spectatorCount():
	'''Number of spectators in server'''
	return len(sbserver.spectators())

def playerCount():
	'''Number of players in game'''
	return len(sbserver.players())

def spectators():
	'''Get list of spectators as Player instances'''
	return cnsToPlayers(sbserver.spectators())

def activePlayers():
	'''Get list of players as Player instances'''
	return cnsToPlayers(sbserver.players())

def player(cn):
	'''Return player instance of cn'''
	try:
		return players[cn]
	except KeyError:
		raise ValueError('Player does not exist')

def playerByName(name):
	'''Return player instance of player with name'''
	for p in all():
		if p.name() == name:
			return p
	raise ValueError('No player by specified name')

@eventHandler('player_disconnect_post')
def playerDisconnect(cn):
	try:
		del players[cn]
	except KeyError:
		logging.error('Player disconnected but does not have player class instance!')

@eventHandler('player_connect_pre')
def playerConnect(cn):
	try:
		del players[cn]
	except KeyError:
		pass
	players[cn] = Player(cn)
	addTimer(1000, triggerServerEvent, ('player_connect_delayed', (cn,)))

@eventHandler('restart_complete')
def reload():
	for cn in sbserver.clients():
		playerConnect(cn)

