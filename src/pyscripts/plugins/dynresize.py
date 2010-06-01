from xsbs.events import eventHandler
from xsbs.players import player, playerCount, spectatorCount
from xsbs.settings import loadPluginConfig
from xsbs.server import maxClients, setMaxClients
import logging

config = {
	'Main':
		{
			# For every n spectators add one to maxclients
			'spectators_addclient_rate': 2
		}
	}

def init():
	loadPluginConfig(config, 'DynamicResize')
	try:
		config['Main']['spectators_addclient_rate'] = int(config['Main']['spectators_addclient_rate'])
	except TypeError:
		logging.error('Non int value for spectator addclient rate.  Setting to 0')
		config['Main']['spectators_addclient_rate'] = 0

adjsize = [0]

@eventHandler('player_spectated')
@eventHandler('player_connect')
@eventHandler('player_disconnect')
@eventHandler('player_unspectated')
def checkSize(cn):
	if config['Main']['spectators_addclient_rate'] == 0:
		return
	newadj = spectatorCount() / config['Main']['spectators_addclient_rate']
	newsize = 0
	if adjsize[0] == newadj:
		return
	elif adjsize[0] > newadj:
		newsize = maxClients() - (adjsize[0] - newadj)
		adjsize[0] = newadj
	else:
		newsize = maxClients() + (newadj - adjsize[0])
		adjsize[0] = newadj
	logging.debug('Adjusting server size to %i due to new spectator', newsize)
	setMaxClients(newsize)
	
init()

