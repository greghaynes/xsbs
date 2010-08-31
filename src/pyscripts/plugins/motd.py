from xsbs.settings import loadPluginConfig
from xsbs.ui import themedict
from xsbs.events import eventHandler
from xsbs.players import player
import string

config = {
	'Templates': {
		'motd': '${emphasis}Welcome to a ${severe_action}XSBS ${emphasis}server, ${client_name}${name}${text}!'
		}
	}

loadPluginConfig(config, 'motd')
motdstring = string.Template(config['Templates']['motd'])

@eventHandler('player_connect_delayed')
def greet(cn):
	p = player(cn)
	p.message(motdstring.substitute(themedict, name=p.name()))
