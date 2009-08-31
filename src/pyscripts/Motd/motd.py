import sbevents, sbserver
import string
from ConfigParser import ConfigParser

motdstring = ''

def greet(cn):
	sbserver.playerMessage(cn, motdstring)

def compilemotd():
	conf = ConfigParser()
	if not conf.read('Motd/plugin.conf'):
		print 'Could not read MOTD config.'
	if not conf.has_option('MOTD', 'template'):
		motdstring = 'Welcome to a XSBS server.'
	else:
		options = conf.options('MOTD')
		formatdict = {}
		for option in options:
			if option != 'template':
				formatdict[option] = conf.get('MOTD', option)
		motdstring = string.Template(conf.get('MOTD', 'template'))
		motdstring = motdstring.substitute(formatdict)
		return motdstring

def init():
	sbevents.registerEventHandler("player_active", greet)

init()
motdstring = compilemotd()

