from xsbs.colors import red
from xsbs.ui import info
from xsbs.colors import colordict
from xsbs.events import eventHandler
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

@eventHandler('player_teamkill')
def teamkill_broadcast(cn, tcn):
	tker = player(cn)
	target = player(tcn)
	serverMessage(info(tktemp.substitute(colordict, tker=tker.name(), victim=target.name(), tkcount=tker.teamkills())))

@eventHandler('player_get_map')
def getmap(cn):
	p = player(cn)
	serverMessage(info(getmaptemp.substitute(colordict, name=p.name())))

@eventHandler('player_uploaded_map')
def onUploadMap(cn):
	p = player(cn)
	serverMessage(info(uptemp.substitute(colordict, name=p.name())))
