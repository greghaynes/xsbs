import sbserver, sbevents, sbtools

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
	sbserver.message(sbtools.red('Duel cancelled.'))

def onMapChange(mapname, mode):
	if currently_dueling[1]:
		currently_dueling[1] = True
		endDuel()

def onPlayerDisconnect(cn):
	if currently_dueling[0] and [duelers[0] == cn or duelers[1] == cn]:
		print 'cancel'
		cancelDuel()
	if cn in duelers:
		duelers[duelers.index(cn)] = -1

def duelCountdown(count, map, mode):
	players = sbserver.players()
	if len(sbserver.players()) != 2 or players[0] not in duelers or players[1] not in duelers:
		cancelDuel()
	elif count == 0:
		currently_dueling[0] = True
		sbserver.message(sbtools.green('Fight!'))
		sbserver.setMap(map, mode)
		sbserver.setPaused(False)
	else:
		sbserver.message(sbtools.green('%i seconds' % count))
		sbevents.timerman.addTimer(1000, duelCountdown, (count-1, map, mode))

def onDuelCommand(cn, args):
	args = args.split(' ')
	if len(args) == 2:
		map = args[0]
		mode = int(args[1])
		players = sbserver.players()
		if len(players) != 2:
			sbserver.message(cn, sbtools.red('There must be only two unspectated players to enter duel mode.'))
			if sbserver.playerPrivilege(cn) > 0:
				sbserver.message(cn, sbtools.red('Use #duel <cn> <cn> to force a duel.'))
		else:
			duelers[0] = players[0]
			duelers[1] = players[1]
			prev_mastermode = sbserver.masterMode()
			sbserver.setMasterMode(2)
			sbserver.message(sbtools.green('Duel begins in...'))
			duelCountdown(5, map, mode)

sbevents.registerCommandHandler('duel', onDuelCommand)
sbevents.registerEventHandler('player_disconnect', onPlayerDisconnect)
sbevents.registerEventHandler('map_changed', onMapChange)

