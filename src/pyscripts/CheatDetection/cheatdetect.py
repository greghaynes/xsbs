import sbserver
from xsbs.events import registerServerEventHandler
from xsbs.players import player
from xsbs.ui import warning

def onMapModified(cn):
	player(cn).gamevars['modified_map'] = True
	checkModified(cn)

def checkModified(cn):
	try:
		if player(cn).gamevars['modified_map']:
			sbserver.playerMessage(cn, warning('You cannot play with a modified map.'))
			sbserver.spectate(cn, cn)
	except KeyError:
		pass

registerServerEventHandler('player_modified_map', onMapModified)
registerServerEventHandler('player_active', checkModified)
registerServerEventHandler('player_unspectated', checkModified)

