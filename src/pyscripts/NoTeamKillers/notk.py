import sbserver, sbevents
from settings import loadConfigFile
from ConfigParser import ConfigParser

limit = 5
duration = 3600

def onTeamkill(cn, tcn):
	if sbserver.playerTeamkills(cn) >= limit:
		sbevents.triggerEvent('player_ban', (cn, duration, 'Teamkilling'))

config = loadConfigFile('notk')
if config.has_option('Config', 'limit'):
	limit = config.get('Config', 'limit')
if config.has_option('Config', 'duration'):
	duration = config.get('Config', 'duration')

sbevents.registerEventHandler('player_teamkill', onTeamkill)

