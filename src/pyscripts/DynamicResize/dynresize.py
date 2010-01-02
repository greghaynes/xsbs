from xsbs.events import eventHandler
from xsbs.players import player, playerCount, spectatorCount
from xsbs.settings import PluginConfig
from sbserver import maxClients, setMaxClients
import logging

config = PluginConfig('DynamicResize')
# For every n spectators add one to maxclients
spectatorsAddClient = config.getOption('Config', 'spectators_addclient_rate', '2')
del config

try:
	spectatorsAddClient = int(spectatorsAddClient)
except TypeError:
	logging.error('Non int value for spectator addclient rate.  Setting to 0')
	spectatorsAddClient = 0

adjsize = [0]

@eventHandler('player_spectated')
@eventHandler('player_connect')
def onSpectate(cn):
	if spectatorsAddClient == 0:
		return
	newadj = spectatorCount() / spectatorsAddClient
	if adjsize[0] != newadj:
		newsize = maxClients() + 1
		logging.info('Adjusting server size to %i due to new spectator', newsize)
		adjsize[0] = newadj
		setMaxClients(newsize)

@eventHandler('player_unspectated')
@eventHandler('player_disconnect')
def onUnspectate(cn):
	if spectatorsAddClient == 0:
		return
	newadj = spectatorCount() / spectatorsAddClient
	if adjsize[0] != newadj:
		newsize = maxClients() - 1
		logging.info('Adjusting server size to %i due to loss of spectator', newsize)
		adjsize[0] = newadj
		setMaxClients(newsize)

