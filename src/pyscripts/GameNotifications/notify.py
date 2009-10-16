import sbserver
from xsbs.colors import red
from xsbs.ui import info
from xsbs.colors import colordict
from xsbs.events import registerServerEventHandler
from xsbs.settings import PluginConfig
import string

config = PluginConfig('gamenotifications')
tktemp = config.getOption('Config', 'teamkill', '${green}${tker}${white} team killed ${orange}${victim}')
uptemp = config.getOption('Config', 'map_uploaded', '${green}${name}${white} uploaded a map. /getmap to receive it')
getmaptemp = config.getOption('Config', 'get_map', '${green}${name}${white} is downloading map')
del config

tktemp = string.Template(tktemp)
uptemp = string.Template(uptemp)
getmaptemp = string.Template(getmaptemp)

def teamkill_broadcast(cn, tcn):
	sbserver.message(info(tktemp.substitute(colordict, tker=sbserver.playerName(cn), victim=sbserver.playerName(tcn))))

def getmap(cn):
	sbserver.message(info(getmaptemp.substitute(colordict, name=sbserver.playerName(cn))))

def onUploadMap(cn):
	sbserver.message(info(uptemp.substitute(colordict, name=sbserver.playerName(cn))))

registerServerEventHandler('player_teamkill', teamkill_broadcast)
registerServerEventHandler('player_uploaded_map', onUploadMap)
registerServerEventHandler('player_get_map', getmap)

