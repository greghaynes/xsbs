import sbserver
from xsbs.settings import PluginConfig
from xsbs.colors import colordict
from xsbs.events import registerServerEventHandler
from xsbs.net import ipLongToString
import string
import pygeoip

db = pygeoip.Database('GeoIp/GeoIP.dat')

conf = PluginConfig('geoip')
template = '${green}${user} ${yellow}has connected from ${orange}${country}'
template = conf.getOption('Config', 'template', template)
del conf

def getCountry(ip): 
	 return db.lookup(ipLongToString(ip)).country

def announce(cn):
	msg = string.Template(template).substitute(colordict, user=sbserver.playerName(cn), country=getCountry(sbserver.playerIpLong(cn)))
	sbserver.message(msg)

registerServerEventHandler("player_connect_delayed", announce)

