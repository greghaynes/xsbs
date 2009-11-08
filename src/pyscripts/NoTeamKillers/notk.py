from Bans.bans import ban
from xsbs.settings import PluginConfig
from xsbs.events import registerServerEventHandler
from xsbs.players import player

config = PluginConfig('notk')
limit = int(config.getOption('Config', 'teamkill_limit', '5'))
duration = int(config.getOption('Config', 'ban_time', '3600'))
del config

def onTeamkill(cn, tcn):
	try:
		if player(cn).teamkills() >= limit:
			ban(cn, duration, 'killing teammates', -1)
	except KeyError:
		pass

registerServerEventHandler('player_teamkill', onTeamkill)

