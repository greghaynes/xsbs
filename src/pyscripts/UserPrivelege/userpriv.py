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
gmtemp = config.getOption('Messages', 'gain_master', '${green}${name}${white} has claimed master')
gatemp = config.getOption('Messages', 'gain_admin', '${green}${name}${white} has claimed admin')
rmtemp = config.getOption('Messages', 'release_master', '${green}${name}${white} has relinquished master')
ratemp = config.getOption('Messages', 'release_admin', '${green}${name}${white} has relinquished admin')
del config
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
		user = loggedInAs(cn)
		if isMaster(user.id):
			sbserver.setMaster(cn)
		else:
			insufficientPermissions(cn)
	except AttributeError:
		sbserver.playerMessage(cn, error('You need to verify using /setmaster before using #master'))

def masterCmd(cn, args):
	return isPlayerMaster(cn)

def onSetMaster(cn, hash):
	if hash == sbserver.hashPassword(cn, sbserver.adminPassword()):
		sbserver.setAdmin(cn)

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

def init():
	registerCommandHandler('master', masterCmd)
	registerServerEventHandler('player_setmaster', onSetMaster)
	registerServerEventHandler('player_setmaster_off', onSetMasterOff)
	registerServerEventHandler('player_claimed_master', onGainMaster)
	registerServerEventHandler('player_claimed_admin', onGainAdmin)
	registerServerEventHandler('player_released_master', onRelMaster)
	registerServerEventHandler('player_released_admin', onRelAdmin)
	Base.metadata.create_all(dbmanager.engine)

init()

