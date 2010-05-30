from xsbs.settings import loadPluginConfig
from xsbs.colors import colordict
from xsbs.ui import info
from xsbs.events import eventHandler
from xsbs.net import ipLongToString
from xsbs.server import message as serverMessage
from xsbs.players import player

import string
from pygeoip import getCountry

config = {
	'Main':
		{
			'connection_nationality_msg': 'yes'
		},
	'Templates':
		{
			'on_connect': '${green}${user}${white} connected from ${orange}${country}',
		}
	}

def init():
	loadPluginConfig(config, 'GeoIp')
	config['Main']['connection_nationality_msg'] = config['Main']['connection_nationality_msg'] == 'yes'
	config['Templates']['on_connect'] = string.Template(config['Templates']['on_connect'])


@eventHandler('player_connect_delayed')
def announce(cn):
	if config['Main']['connection_nationality_msg']:
		p = player(cn)
		msg = config['Templates']['on_connect'].substitute(colordict, user=p.name(), country=getCountry(p.ipLong()))
		serverMessage(info(msg))
	
init()

