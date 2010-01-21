from xsbs.colors import red
from xsbs.ui import info
from xsbs.colors import colordict
from xsbs.events import registerServerEventHandler
from xsbs.settings import PluginConfig
from xsbs.players import player
from xsbs.server import message as serverMessage

import string

config = PluginConfig('gamenotifications')
tktemp = config.getOption('Config', 'teamkill', '${green}${tker}${white} team killed (${tkcount}) ${orange}${victim}')
uptemp = config.getOption('Config', 'map_uploaded', '${green}${name}${white} uploaded a map. /getmap to receive it')
getmaptemp = config.getOption('Config', 'get_map', '${green}${name}${white} is downloading map')
del config

tktemp = string.Template(tktemp)
uptemp = string.Template(uptemp)
getmaptemp = string.Template(getmaptemp)

def teamkill_broadcast(cn, tcn):
	tker = player(cn)
	target = player(tcn)
	serverMessage(info(tktemp.substitute(colordict, tker=tker.name(), victim=target.name(), tkcount=tker.teamkills())))

def getmap(cn):
	serverMessage(info(getmaptemp.substitute(colordict, name=sbserver.playerName(cn))))

def onUploadMap(cn):
	serverMessage(info(uptemp.substitute(colordict, name=sbserver.playerName(cn))))

registerServerEventHandler('player_teamkill', teamkill_broadcast)
registerServerEventHandler('player_uploaded_map', onUploadMap)
registerServerEventHandler('player_get_map', getmap)

