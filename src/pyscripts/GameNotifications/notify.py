import sbserver
from xsbs.colors import red
from xsbs.ui import info
from xsbs.events import registerServerEventHandler

def teamkill(cn, tcn):
	info(red('Player %s has teamkilled %s' % (sbserver.playerName(cn), sbserver.playerName(tcn))))

def getmap(cn):
	info('Player %s is downloading map' % sbserver.playerName(cn))

registerServerEventHandler('player_teamkill', teamkill)
registerServerEventHandler('get_map', getmap)

