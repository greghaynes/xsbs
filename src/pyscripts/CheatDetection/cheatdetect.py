import sbserver
from xsbs.events import registerServerEventHandler
from xsbs.players import player
from xsbs.ui import warning
from xsbs.settings import PluginConfig
from xsbs.commands import registerCommandHandler

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

def mapModifiedSpecCmd(cn, args):
	if args == 'disable':
		spectate_map_modified = False
		sbserver.playerMessage(info('Spectate modified mapes disabled'))
	elif args == 'enable':
		spectate_map_modified = True
		sbserver.playerMessage(info('Spectate modified mapes enabled'))
	else:
		sbserver.playerMessage(cn, error('Usage: #mapmodifiedspec (enable/disable)'))

registerServerEventHandler('player_modified_map', onMapModified)
registerServerEventHandler('player_active', checkModified)
registerServerEventHandler('player_unspectated', checkModified)
registerCommandHandler('mapmodifiedspec', mapModifiedSpecCmd)

