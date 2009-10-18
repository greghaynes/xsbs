import sbserver
from xsbs.events import registerServerEventHandler
from xsbs.players import player
from xsbs.ui import warning
from xsbs.settings import PluginConfig

config = PluginConfig('cheatdetection')
spectate_map_modified = (config.getOption('Config', 'spectate_map_modified', 'yes') == 'yes')
del config

def onMapModified(cn):
	player(cn).gamevars['modified_map'] = True
	checkModified(cn)

def checkModified(cn):
	try:
		if player(cn).gamevars['modified_map'] and spectate_map_modified:
			sbserver.playerMessage(cn, warning('You cannot play with a modified map.'))
			sbserver.spectate(cn)
	except KeyError:
		pass
	except ValueError:
	 	pass

registerServerEventHandler('player_modified_map', onMapModified)
registerServerEventHandler('player_active', checkModified)
registerServerEventHandler('player_unspectated', checkModified)

