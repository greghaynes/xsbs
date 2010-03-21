from xsbs.settings import PluginConfig
from xsbs.colors import colordict
from xsbs.ui import info
from xsbs.events import eventHandler
from xsbs.net import ipLongToString
from xsbs.server import message as serverMessage
from xsbs.players import player

import string
from pygeoip import getCountry

conf = PluginConfig('geoip')
template = '${green}${user}${white} connected from ${orange}${country}'
template = conf.getOption('Config', 'template', template)
del conf


@eventHandler('player_connect_delayed')
def announce(cn):
	p = player(cn)
	msg = string.Template(template).substitute(colordict, user=p.name(), country=getCountry(p.ipLong()))
	serverMessage(info(msg))

