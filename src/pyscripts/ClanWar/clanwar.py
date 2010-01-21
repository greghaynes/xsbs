from xsbs.commands import commandHandler, UsageError, ArgumentValueError
from xsbs.ui import error, notice
from xsbs.colors import green
from xsbs.timers import addTimer
from xsbs.game import modeNumber, currentMode, setMap
from xsbs.server import setPaused
from xsbs.players import player, masterRequired
from xsbs.persistteam import persistentTeams
from xsbs.server import message, setMasterMode

def clanWarTimer(count, cn):
	if count > 0:
		message(notice('Clan war starts in ' + green(str(count))))
		addTimer(1000, clanWarTimer, (count-1, cn))
	else:
		message(notice('Fight!'))
		setPaused(False)

@commandHandler('clanwar')
@masterRequired
def clanWar(cn, args):
	'''@description Start a clan war with current teams
	   @usage map (mode)'''
	sender = player(cn)
	if args == '':
		raise UsageError()
	else:
		args = args.split(' ')
		if len(args) == 1:
			map = args
			mode = currentMode()
		elif len(args) == 2:
			map = args[0]
			try:
				mode = modeNumber(args[1])
			except ValueError:
				raise ArgumentValueError('Invalid game mode')
		persistentTeams(True)
		setMap(map, mode)
		setMasterMode(2)
		setPaused(True, cn)
		clanWarTimer(10, cn)

