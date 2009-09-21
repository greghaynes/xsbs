import sbserver
from xsbs.colors import red
from xsbs.ui import info
from xsbs.colors import colordict
from xsbs.events import registerServerEventHandler
from xsbs.settings import PluginConfig
import string

config = PluginConfig('gamenotifications')
tktemp = config.getOption('Config', 'teamkill', '${red}Player ${green}${tker}${red} has team killed ${orange}${victim}')
del config

tktemp = string.Template(tktemp)

def teamkill(cn, tcn):
	info(tktemp.substitute(colordict, tker=sbserver.playerName(cn), victim=sbserver.playerName(tcn)))

def getmap(cn):
	info('Player %s is downloading map' % sbserver.playerName(cn))

registerServerEventHandler('player_teamkill', teamkill)
registerServerEventHandler('get_map', getmap)

