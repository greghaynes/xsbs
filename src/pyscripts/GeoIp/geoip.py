import sbserver
from xsbs.settings import PluginConfig
from xsbs.colors import colordict
from xsbs.ui import info
from xsbs.events import registerServerEventHandler
from xsbs.net import ipLongToString
import string
import pygeoip

db = pygeoip.GeoIP('GeoIp/GeoIP.dat')

conf = PluginConfig('geoip')
template = '${green}${user} ${white} connected from ${orange}${country}'
template = conf.getOption('Config', 'template', template)
del conf

def getCountry(ip): 
	country = db.country_name_by_addr(ipLongToString(ip))
	if country == '':
		country = 'Unknown'
	return country

def announce(cn):
	msg = string.Template(template).substitute(colordict, user=sbserver.playerName(cn), country=getCountry(sbserver.playerIpLong(cn)))
	sbserver.message(info(msg))

registerServerEventHandler('player_connect_delayed', announce)

