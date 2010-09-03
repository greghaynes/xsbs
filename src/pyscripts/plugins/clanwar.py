from xsbs.commands import commandHandler, UsageError, ArgumentValueError
from xsbs.ui import error, notice, themedict
from xsbs.timers import addTimer
from xsbs.game import modeNumber, currentMode, setMap
from xsbs.server import setPaused
from xsbs.players import player, masterRequired
from xsbs.persistteam import persistentTeams
from xsbs.server import message, setMasterMode, setFrozen
import string

config = {
		'message':'Clan war starts in ${countdowm}${time}${text} seconds.'
	}
config['message'] = string.Template(config['message'])

def clanWarTimer(count, cn):
	if count > 0:
		message(notice(config['message'].substitute(themedict, time=count)))
		addTimer(1000, clanWarTimer, (count-1, cn))
	else:
		message(notice('Fight!'))
		setFrozen(False)
		setPaused(False)

@commandHandler('clanwar')
@masterRequired
def clanWar(sender, args):
	'''@description Start a clan war with current teams
	   @usage map (mode)'''
	if args == '':
		raise UsageError()
	else:
		args = args.split(' ')
		if len(args) == 1:
			map = args[0]
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
		setPaused(True, sender.cn)
		setFrozen(True)
		clanWarTimer(10, sender.cn)

