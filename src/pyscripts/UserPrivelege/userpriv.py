import sbserver
from DB.db import dbmanager
from UserManager.usermanager import User, loggedInAs

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

from xsbs.commands import registerCommandHandler
from xsbs.ui import error, insufficientPermissions
from xsbs.settings import PluginConfig

config = PluginConfig('userprivilege')
tablename = config.getOption('Config', 'tablename', 'userprivileges')
del config

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

def init():
	registerCommandHandler('master', masterCmd)
	Base.metadata.create_all(dbmanager.engine)

init()

