import sbevents, sbserver, sbtools
from settings import PluginConfig
import string


def greet(cn):
	sbserver.playerMessage(cn, motdstring)

config = PluginConfig('motd')
motdstring = config.getOption('Config', 'template', '${orange}Welcome to a ${red}XSBS ${orange}server')
del config
motdstring = string.Template(motdstring).substitute(sbtools.colordict)
sbevents.registerEventHandler("player_active", greet)

