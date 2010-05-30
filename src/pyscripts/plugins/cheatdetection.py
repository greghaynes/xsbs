from xsbs.events import eventHandler
from xsbs.players import player, masterRequired
from xsbs.ui import warning, error, info
from xsbs.settings import loadPluginConfig
from xsbs.commands import commandHandler

config = {
	'Main':
		{
			'spectate_map_modified': 'yes'
		}
	}

def init():
	loadPluginConfig(config, 'CheatDetection')
	config['Main']['spectate_map_modified'] = config['Main']['spectate_map_modified'] == 'yes'

@eventHandler('player_modified_map')
def onMapModified(cn):
	player(cn).gamevars['modified_map'] = True
	checkModified(cn)

@eventHandler('player_active')
@eventHandler('player_unspectated')
def checkModified(cn):
	try:
		p = player(cn)
		if p.gamevars['modified_map'] and config['Main']['spectate_map_modified']:
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
	if args == 'disable':
		config['Main']['spectate_map_modified'] = False
		p.message(info('Spectate modified mapes disabled'))
	elif args == 'enable':
		config['Main']['spectate_map_modified'] = True
		p.message(info('Spectate modified mapes enabled'))
	else:
		p.message(error('Usage: #mapmodifiedspec (enable/disable)'))
		
init()

