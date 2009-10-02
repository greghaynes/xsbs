from xsbs.events import registerServerEventHandler, triggerServerEvent
from xsbs.timers import addTimer
import sbserver

class Player:
	def __init__(self, cn):
		self.cn = cn
		self.gamevars = {}
	def newGame(self):
		del self.gamevars[:]

players = {}

def onMapChanged(mapname, mapmode):
	for player in players.values():
		player.newGame();

def player(cn):
	try:
		return players[cn]
	except KeyError:
		raise ValueError('Player does not exist')

def playerDisconnect(cn):
	try:
		del players[cn]
	except KeyError:
		print 'Player disconnected but does not have player class instance!'

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
registerServerEventHandler('reload_complete', reload)
registerServerEventHandler('map_changed', onMapChanged)

