import sbserver, sbevents, sbtools
import sbplugins

def onPauseCmd(cn, args):
	if args != '':
		sbserver.playerMessage(cn, sbtools.red('Usage: #pause'))
		return
	sbserver.setPaused(True)

def onResumeCmd(cn, args):
	if args != '':
		sbserver.playerMessage(cn, sbtools.red('Usage: #resume'))
		return
	sbserver.setPaused(False)

def onReloadCmd(cn, args):
	if args != '':
		sbserver.playerMessage(cn, sbtools.red('Usage: #reload'))
	else:
		if sbserver.playerPrivilege(cn) > 1:
			sbserver.playerMessage(cn, sbtools.yellow('NOTICE: ') + sbtools.blue('Reloading server plugins.  Fasten your seatbelts...'))
			sbplugins.reload()
		else:
			sbserver.playerMessage(cn, 'Insufficient privileges')

sbevents.registerCommandHandler('pause', onPauseCmd)
sbevents.registerCommandHandler('resume', onResumeCmd)
sbevents.registerCommandHandler('reload', onReloadCmd)

