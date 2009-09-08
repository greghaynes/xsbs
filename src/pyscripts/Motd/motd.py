import sbevents, sbserver, sbtools
import string
from ConfigParser import ConfigParser

motdstring = ''

def greet(cn):
	sbserver.playerMessage(cn, motdstring)

def compilemotd():
	conf = ConfigParser()
	str = ''
	if not conf.read('Motd/plugin.conf'):
		print 'Could not read MOTD config.'
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

