from xsbs.commands import commandHandler, UsageError, ArgumentValueError
from xsbs.ui import error, notice
from xsbs.colors import green
from xsbs.timers import addTimer
from xsbs.game import modeNumber, currentMode, setMap, currentMap
from xsbs.server import setPaused
from xsbs.players import player, masterRequired
from xsbs.persistteam import persistentTeams
from xsbs.server import message, setMasterMode, setFrozen

import sbserver

def duelTimer(count, cn):
	if count > 0:
		message(notice('Duel starts in ' + green(str(count))))
		addTimer(1000, duelTimer, (count-1, cn))
	else:
		message(notice('Duel!'))
		setFrozen(False)
		setPaused(False)

def setupDuel(cn1, cn2, newmode, newmap, sender_cn):
	p1 = player(int(cn1))
	p2 = player(int(cn2))
	for s in sbserver.players():
		sbserver.spectate(s)
	p1.unspectate()
	p2.unspectate()
	persistentTeams(True)	
	setMap(newmap, newmode)
	setMasterMode(2)
	setPaused(True, sender_cn)
	setFrozen(True)
	duelTimer(5, sender_cn)

@commandHandler('duel')
@masterRequired
def duel(sender, args):
	'''@description Start a duel with 2 players and with current teams
	   @usage cn1 cn2 [mode] [map]'''
	if args == '':
		raise UsageError()
		return
	args = args.split(' ')
	if len(args) < 2:
		raise UsageError()
		return
	elif len(args) == 2:
		setupDuel(args[0], args[1], currentMap(), currentMode(), sender.cn)
		return
	elif len(args) == 3:
		try:
			mode = modeNumber(args[2])
		except ValueError:
			raise ArgumentValueError('Invalid game mode')
		else:
			setupDuel(args[0], args[1], mode, currentMap(), sender.cn)
		return
	elif len(args) == 4:
		try:
			mode = modeNumber(args[2])
		except ValueError:
			raise ArgumentValueError('Invalid game mode')
		else:
			setupDuel(args[0], args[1], mode, args[3], sender.cn)
		return
	else:
		raise UsageError()
		return

