from xsbs.players import masterRequired, player
from xsbs.events import eventHandler
from xsbs.commands import commandHandler
import sbserver

def isPaused():
	'''Is the game currently paused'''
	return sbserver.isPaused()

def setPaused(val, cn=-1):
	'''Pause or unpause the game'''
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

@eventHandler('player_pause')
@masterRequired
def onPlayerPause(cn, val):
	setPaused(val, cn)

