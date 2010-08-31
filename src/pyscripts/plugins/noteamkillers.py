from xsbs.ban import ban
from xsbs.settings import loadPluginConfig
from xsbs.events import eventHandler
from xsbs.players import player
from xsbs.ui import warning, themedict
import string

config = {
	'Main':
		{
			'teamkill_limit': 5,
			'ban_time': 3600,
			'warn_tk_limit': 'no',
		},
	'Templates':
		{
			'warn_tk_message': 'This server does not allow more than ${severe_action}${limit}${text} teamkills per game',
		}
	}

def init():
	loadPluginConfig(config, 'NoTK')
	config['Main']['teamkill_limit'] = int(config['Main']['teamkill_limit'])
	config['Main']['ban_time'] = int(config['Main']['ban_time'])
	config['Main']['warn_tk_limit'] = config['Main']['warn_tk_limit'] == 'yes'
	config['Templates']['warn_tk_message'] = string.Template(config['Templates']['warn_tk_message'])

@eventHandler('player_teamkill')
def onTeamkill(cn, tcn):
	try:
		if player(cn).teamkills() >= config['Main']['teamkill_limit']:
			ban(cn, config['Main']['ban_time'], 'killing teammates', -1)
		elif config['Main']['warn_tk_limit'] and player(cn).teamkills() == 1:	
			player(cn).message(warning(config['Templates']['warn_tk_message'].substitute(themedict, limit=config['Main']['teamkill_limit'])))
	except KeyError:
		pass
		
init()
