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

@eventHandler('player_spectated')
@eventHandler('player_unspectated')
def onSpectate(cn):
	if spectatorsAddClient == 0:
		return
	pcount = playerCount()
	speccount = spectatorCount()
	adjpcount = pcount + (speccount / spectatorsAddClient)
	if adjpcount != maxClients():
		logging.info('Adjusting server size by %i due to spectators', adjpcount)
		setMaxClients(adjpcount)

