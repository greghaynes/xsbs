from xsbs.events import eventHandler
from xsbs.players import player, masterRequired
from xsbs.ui import warning, error, info
from xsbs.settings import PluginConfig
from xsbs.commands import commandHandler

config = PluginConfig('cheatdetection')
spectate_map_modified = (config.getOption('Config', 'spectate_map_modified', 'yes') == 'yes')
del config

@eventHandler('player_modified_map')
def onMapModified(cn):
	player(cn).gamevars['modified_map'] = True
	checkModified(cn)

@eventHandler('player_active')
@eventHandler('player_unspectated')
def checkModified(cn):
	try:
		p = player(cn)
		if p.gamevars['modified_map'] and spectate_map_modified:
			p.message(warning('You cannot play with a modified map.'))
			p.spectate()
	except KeyError:
		pass
	except ValueError:
	 	pass

@commandHandler('mapmodifiedspec')
@masterRequired
def mapModifiedSpecCmd(p, args):
	'''@description Enable or disable spectate clients with modified map
	   @usage enable/disable'''
	global spectate_map_modified
	if args == 'disable':
		spectate_map_modified = False
		p.message(info('Spectate modified mapes disabled'))
	elif args == 'enable':
		spectate_map_modified = True
		p.message(info('Spectate modified mapes enabled'))
	else:
		p.message(error('Usage: #mapmodifiedspec (enable/disable)'))

