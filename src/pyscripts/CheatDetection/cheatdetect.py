import sbserver
from xsbs.events import registerServerEventHandler
from xsbs.players import player
from xsbs.ui import info

def onMapModified(cn):
	player(cn).gamevars['modified_map'] = True

def checkModified(cn):
	try:
		if player(cn).gamevars['modified_map']:
			sbserver.playerMessage(cn, info('You cannot play with a modified map.'))
	except KeyError:
		pass

registerServerEventHandler('player_active', checkModified)
registerServerEventHandler('player_unspectated', checkModified)

