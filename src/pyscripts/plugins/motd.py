import sbserver
from xsbs.settings import PluginConfig
from xsbs.colors import colordict
from xsbs.events import eventHandler
import string

@eventHandler('player_connect_delayed')
def greet(cn):
	sbserver.playerMessage(cn, motdstring)

config = PluginConfig('motd')
motdstring = config.getOption('Config', 'template', '${orange}Welcome to a ${red}XSBS ${orange}server')
del config

motdstring = string.Template(motdstring).substitute(colordict)