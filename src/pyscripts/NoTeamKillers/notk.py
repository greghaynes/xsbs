from Bans.bans import ban
from xsbs.settings import PluginConfig
from xsbs.events import eventHandler
from xsbs.players import player
from xsbs.ui import warning
from xsbs.colors import colordict
import string

config = PluginConfig('notk')
limit = int(config.getOption('Config', 'teamkill_limit', '5'))
duration = int(config.getOption('Config', 'ban_time', '3600'))
warn_tk_limit = config.getOption('Config', 'warn_tk_limit', 'no') == 'yes'
warn_tk_message = config.getOption('Config', 'warn_tk_message', 'This server does not allow more than ${red}${limit}${white} teamkills per game')
del config
warn_tk_message = string.Template(warn_tk_message)

@eventHandler('player_teamkill')
def onTeamkill(cn, tcn):
	try:
		if player(cn).teamkills() >= limit:
			ban(cn, duration, 'killing teammates', -1)
		elif warn_tk_limit and player(cn).teamkills() == 1:	
			player(cn).message(warning(warn_tk_message.substitute(colordict, limit=limit)))
	except KeyError:
		pass
