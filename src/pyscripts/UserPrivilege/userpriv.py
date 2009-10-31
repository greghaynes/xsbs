import sbserver
from DB.db import dbmanager
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

def isMaster(user_id):
	try:
		priv = session.query(UserPrivilege).filter(UserPrivilege.user_id==user_id).filter(UserPrivilege.privilege==MASTER).one()
		return True
	except NoResultFound:
		return False

def isPlayerMaster(cn):
	try:
		p = player(cn)
		if p.privilege() > 0:
			return True
		user = loggedInAs(cn)
		if isMaster(user.id):
			return True
		else:
			return False
	except (AttributeError, KeyError):
		return False

class masterRequired(object):
	def __init__(self, func):
		self.func = func
	def __call__(self, *args):
		if sbserver.playerPrivilege(args[0]) == 0 and not isPlayerMaster(args[0]):
			insufficientPermissions(args[0])
		else:
			self.func(*args)

class adminRequired(object):
	def __init__(self, func):
		self.func = func
	def __call__(self, *args):
		if sbserver.playerPrivilege(args[0]) <= 1:
			insufficientPermissions(args[0])
		else:
			self.func(*args)

def masterCmd(cn, args):
	if isPlayerMaster(cn):
		sbserver.setMaster(cn)
	else:
		insufficientPermissions(cn)

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

def userPrivAddCmd(cn, tcn, args):
	if args == 'master':
		if isPlayerMaster(tcn):
			sbserver.playerMessage(cn, error('%s already has master permissions.' % sbserver.playerName(tcn)))
		else:
			try:
				user = loggedInAs(tcn)
			except AttributeError:
				sbserver.playerMessage(cn, error('%s is not logged in.' % sbserver.playerName(tcn)))
			else:
				priv = UserPrivilege(1, user.id)
				session.add(priv)
				session.commit()
				sbserver.playerMessage(cn, info('Master privilege has been given to %s (%s)' % (sbserver.playerName(tcn), user.email)))
	else:
		sbserver.playerMessage(cn, error('Privilege level must be \'master\''))

def userPrivDelCmd(cn, tcn, args):
	sbserver.playerMessage(cn, error('Not yet implemented.'))

@adminRequired
def onUserPrivCmd(cn, args):
	sp = args.split(' ')
	tcn = int(sp[0])
	subcmd = sp[1]
	args = args[len(sp[0])+len(sp[1])+2:]
	if subcmd == 'add':
		userPrivAddCmd(cn, tcn, args)
	elif subcmd == 'del':
		userPrivDelCmd(cn, tcn, args)
	else:
		sbserver.playerMessage(cn, error('Usage: #userpriv <cn> <action> <level>'))

def init():
	registerCommandHandler('master', masterCmd)
	registerCommandHandler('userpriv', onUserPrivCmd)
	registerServerEventHandler('player_setmaster', onSetMaster)
	registerServerEventHandler('player_setmaster_off', onSetMasterOff)
	registerServerEventHandler('player_claimed_master', onGainMaster)
	registerServerEventHandler('player_claimed_admin', onGainAdmin)
	registerServerEventHandler('player_released_master', onRelMaster)
	registerServerEventHandler('player_released_admin', onRelAdmin)
	registerServerEventHandler('player_auth_succeed', onAuthSuccess)
	Base.metadata.create_all(dbmanager.engine)

init()

