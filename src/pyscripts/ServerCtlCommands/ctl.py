import sbserver
from xsbs.commands import registerCommandHandler
from xsbs.colors import red, yellow, blue
from xsbs.plugins import reload as pluginReload

def onPauseCmd(cn, args):
	if args != '':
		sbserver.playerMessage(cn, red('Usage: #pause'))
		return
	sbserver.setPaused(True)

def onResumeCmd(cn, args):
	if args != '':
		sbserver.playerMessage(cn, red('Usage: #resume'))
		return
	sbserver.setPaused(False)

def onReloadCmd(cn, args):
	if args != '':
		sbserver.playerMessage(cn, red('Usage: #reload'))
	else:
		if sbserver.playerPrivilege(cn) > 1:
			sbserver.playerMessage(cn, yellow('NOTICE: ') + blue('Reloading server plugins.  Fasten your seatbelts...'))
			pluginReload()
		else:
			sbserver.playerMessage(cn, 'Insufficient privileges')

registerCommandHandler('pause', onPauseCmd)
registerCommandHandler('resume', onResumeCmd)
registerCommandHandler('reload', onReloadCmd)

