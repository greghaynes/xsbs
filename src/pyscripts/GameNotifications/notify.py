import sbserver
from xsbs.colors import red
from xsbs.ui import info
from xsbs.colors import colordict
from xsbs.events import registerServerEventHandler
from xsbs.settings import PluginConfig
import string

config = PluginConfig('gamenotifications')
tktemp = config.getOption('Config', 'teamkill', '$Player ${green}${tker}${white} has team killed ${orange}${victim}')
del config

if tktemp == 'None':
	tk_broadcast = 0
elif tktemp == 'Master':
	tk_broadgast = 1
else:
	tk_broadcast = 2

if tk_broadcast > 0:
	tktemp = string.Template(tktemp)

def teamkill_broadcast(cn, tcn):
	sbserver.message(info(tktemp.substitute(colordict, tker=sbserver.playerName(cn), victim=sbserver.playerName(tcn))))

def getmap(cn):
	sbserver.message(info('%s is downloading map' % sbserver.playerName(cn)))

registerServerEventHandler('player_teamkill', teamkill_broadcast)
registerServerEventHandler('get_map', getmap)

