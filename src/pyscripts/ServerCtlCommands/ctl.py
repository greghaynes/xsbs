import sbserver

from xsbs.events import triggerServerEvent
from xsbs.commands import commandHandler, UsageError, ExtraArgumentError, StateError
from xsbs.settings import PluginConfig
from xsbs.colors import red, yellow, blue, green, white, colordict
from xsbs.plugins import reloadPlugins
from xsbs.ui import error, info, notice, insufficientPermissions
from xsbs.net import ipLongToString
from xsbs.users import loggedInAs
from xsbs.users.privilege import isUserMaster, isUserAdmin, UserPrivilege
from xsbs.players import masterRequired, adminRequired, player, currentAdmin
from xsbs.server import setPaused, message as sendServerMessage
from xsbs.db import dbmanager
from xsbs.timers import addTimer

from Motd.motd import motdstring
import string

config = PluginConfig('servercommands')
servermsg_template = config.getOption('Templates', 'servermsg', '${orange}${sender}${white}: ${message}')
pm_template = config.getOption('Templates', 'pm', '${orange}${sender}${white}: ${message}')
smite_template = config.getOption('Templates', 'smite', '${green}${smited}${white} has been smited by ${orange}${smiter}')
resume_timeout = int(config.getOption('Config', 'resume_timeout', 5))
del config
servermsg_template = string.Template(servermsg_template)
pm_template = string.Template(pm_template)
smite_template = string.Template(smite_template)

session = dbmanager.session()

@commandHandler('pause')
@masterRequired
def onPauseCmd(cn, args):
	'''@description Pause the game
	   @usage'''
	if args != '':
		raise ExtraArgumentError()
		return
	setPaused(True, cn)


def resumeTimer(count, cn):
	if count > 0:
		sendServerMessage(notice('Resuming in ' + green(str(count)) + white('...')))
		addTimer(1000, resumeTimer, (count-1, cn))
	else:
		setPaused(False, cn)

@commandHandler('resume')
@masterRequired
def onResumeCmd(cn, args):
	'''@description Resume game from pause
	   @usage
	   @master'''
	if args != '':
		raise ExtraArgumentError()
		return
	if resume_timeout > 0:
		resumeTimer(resume_timeout, cn)
	else:
		setPaused(False, cn)

@commandHandler('reload')
@adminRequired
def onReloadCmd(cn, args):
	'''@description Reload server plugins
	   @usage
	   @admin'''
	if args != '':
		raise ExtraArgumentError()
	else:
		sbserver.playerMessage(cn, yellow('NOTICE: ') + blue('Reloading server plugins.  Fasten your seatbelts...'))
		reloadPlugins()

@commandHandler('givemaster')
@masterRequired
def onGiveMaster(cn, args):
	'''@description Give master to a client
	   @usage cn
	   @master'''
	if args == '':
		raise UsageError()
		return
	try:
		tcn = int(args)
	except TypeError:
		raise UsageError()
		return
	sbserver.playerMessage(cn, info('You have given master to %s') % sbserver.playerName(tcn))
	sbserver.setMaster(tcn)

@commandHandler('resize')
@adminRequired
def onResize(cn, args):
	'''@description Change maximum clients allowed in server
	   @usage maxclients
	   @admin'''
	if args == '':
		raise UsageError()
	else:
		size = int(args)
		sbserver.setMaxClients(int(args))

@commandHandler('minsleft')
@masterRequired
def onMinsLeft(cn, args):
	'''@description Set minutes left in current match
	   @usage minutes
	   @master'''
	if args == '':
		raise UsageError()
	else:
		sbserver.setMinsRemaining(int(args))

@commandHandler('specall')
@masterRequired
def specAll(cn, args):
	'''@description Make all clients spectators
	   @usage
	   @master'''
	if args != '':
		raise ExtraArgumentError()
	else:
		for s in sbserver.players():
			sbserver.spectate(s)

@commandHandler('unspecall')
@masterRequired
def unspecAll(cn, args):
	'''@description Make all clients players
	   @usage
	   @master'''
	if args != '':
		raise ExtraArgumentError()
	else:
		for s in sbserver.spectators():
			sbserver.unspectate(s)

@commandHandler('servermsg')
@masterRequired
def serverMessage(cn, args):
	'''@description Broadcast message to all clients in server
	   @usage message
	   @master'''
	if args == '':
		raise UsageError()
	else:
		msg = servermsg_template.substitute(colordict, sender=sbserver.playerName(cn), message=args)
		sbserver.message(msg)

@commandHandler('ip')
@masterRequired
def playerIp(cn, args):
	'''@description Get string representation of client ip
	   @usage cn
	   @master'''
	if args == '':
		raise UsageError()
	else:
		sbserver.message(info(player(int(args)).ipString()))

# user commands

@commandHandler('master')
@masterRequired
def masterCmd(cn, args):
	'''@description Claim master
	   @usage
	   @master'''
	if args != '':
		raise ExtraArgumentError()
	if currentAdmin() != None:
		raise StateError('Admin is present')
	if sbserver.playerPrivilege(cn) == 0:
		sbserver.setMaster(cn)

@commandHandler('admin')
@adminRequired
def adminCmd(cn, args):
	'''@description Claim master
	   @usage
	   @admin'''
	if args != '':
		raise ExtraArgumentError()
	if sbserver.playerPrivilege(cn) == 0 or sbserver.playerPrivilege(cn) == 1:
		sbserver.setAdmin(cn)

@commandHandler('unsetmaster')
@masterRequired
def unsetMaster(cn, args):
	'''@description Force release master from current master
	   @usage
	   @master'''
	if args != '':
		raise ExtraArgumentError()
	else:
		sbserver.setMaster(-1)

def userPrivSetCmd(cn, tcn, args):
	user_id = player(tcn).user.id
	if args == 'user':
		try:
			if isUser(player(tcn).user.id):
				sbserver.playerMessage(cn, error('%s already has user permissions.' % sbserver.playerName(tcn)))
				return
		except (ValueError, AttributeError):
			pass
		else:
			try:
				user = loggedInAs(tcn)
			except AttributeError:
				sbserver.playerMessage(cn, error('%s is not logged in.' % sbserver.playerName(tcn)))
			else:
				dbmanager.query(UserPrivilege).filter(UserPrivilege.user_id==user_id).update({ 'privilege': None })
				session.add(UserPrivilege(0, user.id))
				session.commit()
				sbserver.playerMessage(cn, info('User privilege has been given to %s (%s)' % (sbserver.playerName(tcn), user.email)))
	elif args == 'master':
		try:
			if isUserMaster(player(tcn).user.id):
				sbserver.playerMessage(cn, error('%s already has master permissions.' % sbserver.playerName(tcn)))
				return
		except (ValueError, AttributeError):
			pass
		else:
			try:
				user = loggedInAs(tcn)
			except AttributeError:
				sbserver.playerMessage(cn, error('%s is not logged in.' % sbserver.playerName(tcn)))
			else:
				dbmanager.query(UserPrivilege).filter(UserPrivilege.user_id==user_id).update({ 'privilege': None })
				session.add(UserPrivilege(1, user.id))
				session.commit()
				sbserver.playerMessage(cn, info('Master privilege has been given to %s (%s)' % (sbserver.playerName(tcn), user.email)))
	elif args == 'admin':
		try:
			if isUserAdmin(player(tcn).user.id):
				sbserver.playerMessage(cn, error('%s already has admin permissions.' % sbserver.playerName(tcn)))
				return
		except (ValueError, AttributeError):
			pass
		else:
			try:
				user = loggedInAs(tcn)
			except AttributeError:
				sbserver.playerMessage(cn, error('%s is not logged in.' % sbserver.playerName(tcn)))
			else:
				dbmanager.query(UserPrivilege).filter(UserPrivilege.user_id==user_id).update({ 'privilege': None })
				session.add(UserPrivilege(2, user.id))
				session.commit()
				sbserver.playerMessage(cn, info('Admin privilege has been given to %s (%s)' % (sbserver.playerName(tcn), user.email)))
	else:
		sbserver.playerMessage(cn, error('Privilege level must be \'master\' to set master permissions and \'admin\' to set master or admin permissions'))

@commandHandler('userpriv')
@adminRequired
def onUserPrivCmd(cn, args):
	'''@description Set privileges for server account
	   @usage <cn> <action> <level>
	   @admin'''
	sp = args.split(' ')
	try:
		if sp[0] == 'set':
			subcmd = sp[0]
			tcn = int(sp[2])
			args = sp[1]
		elif sp[0] == 'wipe':
			subcmd = sp[0]
			tcn = int(sp[1])
			args = 'user'
		else:
			subcmd = sp[1]
			tcn = int(sp[0])
			args = sp[2]
	except ValueError:
		raise UsageError()

	if subcmd == 'add':
		userPrivSetCmd(cn, tcn, args)
	elif subcmd == 'del':
		userPrivSetCmd(cn, tcn, 'user')
	elif subcmd == 'set':
		userPrivSetCmd(cn, tcn, args)
	elif subcmd == 'wipe':
		userPrivSetCmd(cn, tcn, args)
	else:
		raise UsageError()

@commandHandler('pm')
def onPmCommand(cn, args):
	'''@description Send a private message
	   @usage <cn> <message>
	   @public'''
	args = args.split()
	if len(args) < 2:
		raise UsageError()
	i = 0
	for key in args:
		if i > 1:
			args[1] += (" " + str(key))
		i += 1
	player(int(args[0])).message(pm_template.substitute(colordict, sender=player(cn).name(), message=args[1]))

@commandHandler('smite')
@masterRequired
def onSmiteCommand(cn, args):
	'''@description Strike a player down
	   @usage <cn>
	   @master'''
	if args == '':
		raise UsageError()
	p = player(cn)
	t = player(int(args))
	sendServerMessage(info(smite_template.substitute(colordict, smiter=p.name(), smited=t.name())))
	t.suicide()


