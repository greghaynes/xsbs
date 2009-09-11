import sbserver, sbevents, sbtools

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

sbevents.registerCommandHandler('pause', onPauseCmd)
sbevents.registerCommandHandler('resume', onResumeCmd)

