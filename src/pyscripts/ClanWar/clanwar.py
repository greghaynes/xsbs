from xsbs.commands import commandHandler
from xsbs.ui import error, notice
from xsbs.colors import green
from xsbs.timers import addTimer
from xsbs.game import modeNumber
from xsbs.players import player
from UserPrivilege.userpriv import masterRequired
import sbserver

def clanWarTimer(count):
	if count > 0:
		sbserver.message(notice('Clan war starts in ' + green(str(count))))
		addTimer(1000, clanWarTimer, (count-1,))
	else:
		sbserver.message(notice('Fight!'))
		sbserver.setPaused(False)

@commandHandler('clanwar')
def clanWar(cn, args):
	sender = player(cn)
	if args == '':
		sender.message(error('Usage: #clanwar <map> (mode)'))
	else:
		args = args.split(' ')
		if len(args) == 1:
			map = args
			mode = sbserver.gameMode()
		elif len(args) == 2:
			map = args[0]
			try:
				mode = modeNumber(args[1])
			except ValueError:
				sender.message(error('Invalid game mode'))
				return
		sbserver.setMap(map, mode)
		sbserver.setMasterMode(2)
		sbserver.setPaused(True)
		clanWarTimer(10)

