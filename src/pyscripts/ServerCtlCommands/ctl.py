import sbserver
from xsbs.commands import registerCommandHandler
from xsbs.colors import red, yellow, blue, green
from xsbs.plugins import reload as pluginReload
from Motd.motd import motdstring

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

def onInfoCmd(cn, args):
	sbserver.playerMessage(cn, motdstring)

def onGiveMaster(cn, args):
	if args == '':
		sbserver.playerMessage(cn, red('Usage #givemaster <cn>'))
		return
	try:
		tcn = int(args)
	except TypeError:
		sbserver.playerMessage(cn, red('Usage #givemaster <cn>'))
		return
	if sbserver.playerPrivilege(cn) > 0:
		sbserver.playerMessage(cn, green('You have given master to %s') % sbserver.playerName(tcn))
		sbserver.setMaster(tcn)
	else:
		sbserver.playerMessage(cn, red('Insufficient permissions.'))

registerCommandHandler('pause', onPauseCmd)
registerCommandHandler('resume', onResumeCmd)
registerCommandHandler('reload', onReloadCmd)
registerCommandHandler('info', onInfoCmd)
registerCommandHandler('givemaster', onGiveMaster)

