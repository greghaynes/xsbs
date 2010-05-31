from xsbs.players import masterRequired, player
from xsbs.events import eventHandler
from xsbs.commands import commandHandler, StateError
from xsbs.ui import notice
from xsbs.colors import colordict
from xsbs.settings import loadPluginConfig

import string
import sbserver

config = {
	'Templates':
		{
			'action_message': 'The game has been ${action} by ${orange}${name}',
		}
	}

def init():
	loadPluginConfig(config, 'ServerCmds')
	config['Templates']['action_message'] = string.Template(config['Templates']['action_message'])

mastermodes = [
	'open',
	'veto',
	'locked',
	'private',
]

def isPaused():
	'''Is the game currently paused'''
	return sbserver.isPaused()

def setPaused(val, cn=-1):
	'''Pause or unpause the game'''
	if isFrozen():
		raise StateError('Server is currently frozen')
	if val == isPaused():
		return
	if val:
		action = 'paused'
	else:
		action = 'unpaused'
	try:
		p = player(cn)
	except ValueError:
		name = 'Unknown'
	else:
		name = p.name()
	sbserver.message(notice(pause_message.substitute(
		colordict,
		action=action,
		name=name)))
	sbserver.setPaused(val)

def adminPassword():
	'''Administrator password of server.'''
	return sbserver.adminPassword()

def ip():
	'''Ip address server is bound to.'''
	return sbserver.ip()

def port():
	'''Port server is bound to.'''
	return sbserver.port()

def reload():
	'''Reload python system.'''
	return sbserver.reload()

def setBotLimit(limit):
	'''Set maximum number of bots.'''
	return sbserver.setBotLimit(limit)

def uptime():
	'''Server uptime in miliseconds.'''
	return sbserver.uptime()

def message(string):
	'''Send message to server.'''
	sbserver.message(string)

def setMasterMode(mm_number):
	'''Set server master mode.
	   0 - open
	   1 - veto
	   2 - locked
	   3 - private'''
	sbserver.setMasterMode(mm_number)

def masterModeName(mm_number):
	'''Name of the master mode number'''
	return mastermodes[mm_number]

def maxClients():
	'''Maximum clients allowed in server.'''
	return sbserver.maxClients()

def setMaxClients(num_clients):
	'''Set the maximum clients allowed in server.'''
	return sbserver.setMaxClients(num_clients)

server_frozen = [False]

def setFrozen(val):
	'''Sets wether the server state is frozen.
	   This value is recognized by many of the server
	   commands (such as pause/unpause) and setting this
	   to true will keep them from functioning.'''
	server_frozen[0] = val

def isFrozen():
	'''Is the currently frozen.  See setFrozen(val).'''
	return server_frozen[0]

@eventHandler('player_pause')
@masterRequired
def onPlayerPause(cn, val):
	setPaused(val, cn)

def cseval(data):
	return sbserver.cseval(data)

def csevalfile(file):
	f = open(file, "r")
	try:
		cseval(f.read())
	except: pass
	finally:
		f.close()
		
init()
