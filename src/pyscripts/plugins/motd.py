from xsbs.settings import loadPluginConfig
from xsbs.colors import colordict
from xsbs.events import eventHandler
from xsbs.players import player
import string

#config = PluginConfig('motd')
#motdstring = config.getOption('Config', 'template', '${orange}Welcome to a ${red}XSBS ${orange}server, ${green}${name}${white}!')

config = {
	'Templates': {
		'motd': '${orange}Welcome to a ${red}XSBS ${orange}server, ${green}${name}${white}!'
		}
	}

loadPluginConfig(config, 'motd')
motdstring = string.Template(config['Templates']['motd'])

@eventHandler('player_connect_delayed')
def greet(cn):
	p = player(cn)
	p.message(motdstring.substitute(colordict, name=p.name()))
