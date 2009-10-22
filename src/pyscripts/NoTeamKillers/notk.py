import sbserver
from Bans.bans import ban
from xsbs.settings import PluginConfig
from xsbs.events import registerServerEventHandler

config = PluginConfig('notk')
limit = int(config.getOption('Config', 'teamkill_limit', '5'))
duration = int(config.getOption('Config', 'ban_time', '3600'))
del config

def onTeamkill(cn, tcn):
	if sbserver.playerTeamkills(cn) >= limit:
		ban(cn, duration, 'killing teammates', -1)

registerServerEventHandler('player_teamkill', onTeamkill)

