import sbserver
from xsbs.colors import red, green
from xsbs.ui import info, error
from xsbs.timers import addTimer
from xsbs.events import registerServerEventHandler
from xsbs.commands import registerCommandHandler

currently_dueling = [False, False]
prev_mastermode = 0
duelers = [-1, -1]

def endDuel():
	sbserver.setMasterMode(prev_mastermode)
	sbserver.setPaused(False)
	currently_dueling[0] = False
	currently_dueling[1] = False

def finishDuel():
	endDuel()

def cancelDuel():
	endDuel()
	sbserver.message(info('Duel cancelled.'))

def onMapChange(mapname, mode):
	if currently_dueling[1]:
		currently_dueling[1] = True
		endDuel()

def onPlayerDisconnect(cn):
	if currently_dueling[0] and (duelers[0] == cn or duelers[1] == cn):
		cancelDuel()

def duelCountdown(count, map, mode):
	players = sbserver.players()
	if len(sbserver.players()) != 2 or players[0] not in duelers or players[1] not in duelers:
		cancelDuel()
	elif count == 0:
		currently_dueling[0] = True
		sbserver.message(green('Fight!'))
		sbserver.setMap(map, mode)
		sbserver.setPaused(False)
	else:
		sbserver.message(green('%i seconds' % count))
		addTimer(1000, duelCountdown, (count-1, map, mode))

def onDuelCommand(cn, args):
	if args == '':
		sbserver.playerMessage(cn, error('Usage: #duel <mapname> (mode) (cn) (cn)'))
	args = args.split(' ')
	players = sbserver.players()
	if len(players) != 2:
		sbserver.playerMessage(cn, error('There must be only two unspectated players to enter duel mode.'))
	else:
		if len(args) == 2:
			map = args[0]
			mode = int(args[1])
		elif len(args) == 1:
			map = args[0]
			mode = sbserver.gameMode()
		else:
			sbserver.playerMessage(cn, error('Usage: #duel <mapname> (mode)'))
			return
		duelers[0] = players[0]
		duelers[1] = players[1]
		prev_mastermode = sbserver.masterMode()
		sbserver.setMasterMode(2)
		sbserver.message(green('Duel begins in...'))
		duelCountdown(5, map, mode)

registerCommandHandler('duel', onDuelCommand)
registerServerEventHandler('player_disconnect', onPlayerDisconnect)
registerServerEventHandler('map_changed', onMapChange)

