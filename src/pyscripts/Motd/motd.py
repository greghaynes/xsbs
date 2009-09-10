import sbevents, sbserver, sbtools
from settings import loadConfigFile
import string

motdstring = ''

def greet(cn):
	sbserver.playerMessage(cn, motdstring)

def compilemotd():
	conf = loadConfigFile('motd')
	if not conf.has_option('MOTD', 'template'):
		str = 'Welcome to a XSBS server.'
	else:
		str = conf.get('MOTD', 'template')
		str = string.Template(str).substitute(sbtools.colordict)
	del conf
	return str

def init():
	sbevents.registerEventHandler("player_active", greet)

motdstring = compilemotd()
init()

