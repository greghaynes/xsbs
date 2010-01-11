import sbserver
from UserManager.usermanager import User, loggedInAs

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

from xsbs.commands import registerCommandHandler
from xsbs.events import registerServerEventHandler
from xsbs.ui import error, info, insufficientPermissions
from xsbs.colors import colordict
from xsbs.settings import PluginConfig
from xsbs.players import player
from xsbs.db import dbmanager
import string

config = PluginConfig('userprivilege')
tablename = config.getOption('Config', 'tablename', 'userprivileges')
authtemp = config.getOption('Messages', 'authenticated', '${green}${name}${white} authenticated as ${magenta}${authname}')
gmtemp = config.getOption('Messages', 'gain_master', '${green}${name}${white} claimed ${red}master')
gatemp = config.getOption('Messages', 'gain_admin', '${green}${name}${white} claimed ${red}admin')
rmtemp = config.getOption('Messages', 'release_master', '${green}${name}${white} relinquished ${red}master')
ratemp = config.getOption('Messages', 'release_admin', '${green}${name}${white} relinquished ${red}admin')
del config
authtemp = string.Template(authtemp)
gmtemp = string.Template(gmtemp)
gatemp = string.Template(gatemp)
rmtemp = string.Template(rmtemp)
ratemp = string.Template(ratemp)

Base = declarative_base()
session = dbmanager.session()

USER = 0
MASTER = 1
ADMIN = 2

class UserPrivilege(Base):
	__tablename__ = tablename
	id = Column(Integer, primary_key=True)
	privilege = Column(Integer)
	user_id = Column(Integer)
	def __init__(self, privilege, user_id):
		self.privilege = privilege
		self.user_id = user_id

def isUser(user_id):
	try:
		priv = session.query(UserPrivilege).filter(UserPrivilege.user_id==user_id).filter(UserPrivilege.privilege==USER).one()
		return True
	except NoResultFound:
		return False


def isMaster(user_id):
	try:
		priv = session.query(UserPrivilege).filter(UserPrivilege.user_id==user_id).filter(UserPrivilege.privilege==MASTER).one()
		return True
	except NoResultFound:
		return False
		
def isAdmin(user_id):
	try:
		priv = session.query(UserPrivilege).filter(UserPrivilege.user_id==user_id).filter(UserPrivilege.privilege==ADMIN).one()
		return True
	except NoResultFound:
		return False


def isPlayerMaster(cn):
	try:
		p = player(cn)
		if p.privilege() ==1:
			return True
		user = loggedInAs(cn)
		if isMaster(user.id):
			return True
		else:
			return False
	except (AttributeError, KeyError):
		return False
		
def isPlayerAdmin(cn):
	try:
		p = player(cn)
		if p.privilege() > 1:
			return True
		user = loggedInAs(cn)
		if isAdmin(user.id):
			return True
		else:
			return False
	except (AttributeError, KeyError):
		return False


class masterRequired(object):
	def __init__(self, func):
		self.func = func
		self.__doc__ = func.__doc__
		self.__name__ = func.__name__
	def __call__(self, *args):
		if sbserver.playerPrivilege(args[0]) == 0 and not isPlayerMaster(args[0]) and not isPlayerAdmin(args[0]):
			insufficientPermissions(args[0])
		else:
			self.func(*args)

class adminRequired(object):
	def __init__(self, func):
		self.func = func
		self.__doc__ = func.__doc__
		self.__name__ = func.__name__
	def __call__(self, *args):
		if sbserver.playerPrivilege(args[0]) <= 1 and not isPlayerAdmin(args[0]):
			insufficientPermissions(args[0])
		else:
			self.func(*args)

@masterRequired
def masterCmd(cn, args):
	'''@description Claim master
	   @usage'''
	sbserver.setMaster(cn)

@masterRequired
def unsetMaster(cn, args):
	'''@description Force release master from current master
	   @usage'''
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #unsetmaster'))
	else:
		sbserver.setMaster(-1)

def onSetMaster(cn, hash):
	if hash == sbserver.hashPassword(cn, sbserver.adminPassword()):
		sbserver.setAdmin(cn)

def onAuthSuccess(cn, name):
	sbserver.message(info(authtemp.substitute(colordict, name=sbserver.playerName(cn), authname=name)))
	sbserver.setMaster(cn)

def onSetMasterOff(cn):
	sbserver.resetPrivilege(cn)

def onGainMaster(cn):
	sbserver.message(info(gmtemp.substitute(colordict, name=sbserver.playerName(cn))))

def onGainAdmin(cn):
	sbserver.message(info(gatemp.substitute(colordict, name=sbserver.playerName(cn))))

def onRelMaster(cn):
	sbserver.message(info(rmtemp.substitute(colordict, name=sbserver.playerName(cn))))

def onRelAdmin(cn):
	sbserver.message(info(ratemp.substitute(colordict, name=sbserver.playerName(cn))))

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
				session.query(UserPrivilege).filter(UserPrivilege.user_id==user_id).update({ 'privilege': None })
				session.add(UserPrivilege(0, user.id))
				session.commit()
				sbserver.playerMessage(cn, info('User privilege has been given to %s (%s)' % (sbserver.playerName(tcn), user.email)))
	elif args == 'master':
		try:
			if isMaster(player(tcn).user.id):
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
				session.query(UserPrivilege).filter(UserPrivilege.user_id==user_id).update({ 'privilege': None })
				session.add(UserPrivilege(1, user.id))
				session.commit()
				sbserver.playerMessage(cn, info('Master privilege has been given to %s (%s)' % (sbserver.playerName(tcn), user.email)))
	elif args == 'admin':
		try:
			if isAdmin(player(tcn).user.id):
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
				session.query(UserPrivilege).filter(UserPrivilege.user_id==user_id).update({ 'privilege': None })
				session.add(UserPrivilege(2, user.id))
				session.commit()
				sbserver.playerMessage(cn, info('Admin privilege has been given to %s (%s)' % (sbserver.playerName(tcn), user.email)))
	else:
		sbserver.playerMessage(cn, error('Privilege level must be \'master\' to set master permissions and \'admin\' to set master or admin permissions'))

@adminRequired
def onUserPrivCmd(cn, args):
	'''@description Set privileges for server account
		@usage <cn> <action> <level>'''
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
		raise UsageError('#userpriv set <level> <cn>')

	if subcmd == 'add':
		userPrivSetCmd(cn, tcn, args)
	elif subcmd == 'del':
		userPrivSetCmd(cn, tcn, 'user')
	elif subcmd == 'set':
		userPrivSetCmd(cn, tcn, args)
	elif subcmd == 'wipe':
		userPrivSetCmd(cn, tcn, args)
	else:
		sbserver.playerMessage(cn, error('Usage: #userpriv set <level> <cn>'))

def init():
	registerCommandHandler('master', masterCmd)
	registerCommandHandler('userpriv', onUserPrivCmd)
	registerCommandHandler('unsetmaster', unsetMaster)
	registerServerEventHandler('player_setmaster', onSetMaster)
	registerServerEventHandler('player_setmaster_off', onSetMasterOff)
	registerServerEventHandler('player_claimed_master', onGainMaster)
	registerServerEventHandler('player_claimed_admin', onGainAdmin)
	registerServerEventHandler('player_released_master', onRelMaster)
	registerServerEventHandler('player_released_admin', onRelAdmin)
	registerServerEventHandler('player_auth_succeed', onAuthSuccess)
	Base.metadata.create_all(dbmanager.engine)

init()
