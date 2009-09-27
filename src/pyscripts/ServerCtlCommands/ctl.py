import sbserver
from xsbs.events import triggerServerEvent
from xsbs.commands import registerCommandHandler
from xsbs.colors import red, yellow, blue, green
from xsbs.plugins import reload as pluginReload
from xsbs.ui import error, info, insufficientPermissions
from Motd.motd import motdstring

def onPauseCmd(cn, args):
	if sbserver.playerPrivilege(cn) == 0:
		insufficientPermissions(cn)
		return
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #pause'))
		return
	sbserver.setPaused(True)

def onResumeCmd(cn, args):
	if sbserver.playerPrivilege(cn) == 0:
		insufficientPermissions(cn)
		return
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #resume'))
		return
	sbserver.setPaused(False)

def onReloadCmd(cn, args):
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #reload'))
	else:
		if sbserver.playerPrivilege(cn) > 1:
			sbserver.playerMessage(cn, yellow('NOTICE: ') + blue('Reloading server plugins.  Fasten your seatbelts...'))
			pluginReload()
		else:
			sbserver.playerMessage(cn, error('Insufficient privileges'))

def onInfoCmd(cn, args):
	sbserver.playerMessage(cn, motdstring)

def onGiveMaster(cn, args):
	if args == '':
		sbserver.playerMessage(cn, error('Usage #givemaster <cn>'))
		return
	try:
		tcn = int(args)
	except TypeError:
		sbserver.playerMessage(cn, error('Usage #givemaster <cn>'))
		return
	if sbserver.playerPrivilege(cn) > 0:
		sbserver.playerMessage(cn, info('You have given master to %s') % sbserver.playerName(tcn))
		sbserver.setMaster(tcn)
	else:
		sbserver.playerMessage(cn, error('Insufficient permissions.'))

def onMasterMask(cn, args):
	if args == '':
		sbserver.playerMessage(cn, error('Usage: #mastermask <int>'))
		return
	if sbserver.playerPrivilege(cn) != 2:
		sbserver.playerMessage(cn, error('Insufficient permissions.'))
		return
	args = args.split(' ')
	sbserver.setMasterMask(int(args[0]))
	sbserver.message(info('Master mask is now %s') % args[0])

registerCommandHandler('pause', onPauseCmd)
registerCommandHandler('resume', onResumeCmd)
registerCommandHandler('reload', onReloadCmd)
registerCommandHandler('info', onInfoCmd)
registerCommandHandler('givemaster', onGiveMaster)
registerCommandHandler('mastermask', onMasterMask)

