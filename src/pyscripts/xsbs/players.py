from xsbs.events import registerServerEventHandler
import sbserver

class Player:
	def __init__(self, cn):
		self.cn = cn

players = {}

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

