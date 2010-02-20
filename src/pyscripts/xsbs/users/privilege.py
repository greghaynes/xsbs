import sbserver

from elixir import Entity, Field, String, Integer, Boolean, ManyToOne, OneToMany, setup_all, session
from sqlalchemy.orm.exc import NoResultFound

from xsbs.events import registerServerEventHandler
from xsbs.ui import error, info, insufficientPermissions
from xsbs.colors import colordict
from xsbs.settings import PluginConfig
import string

config = PluginConfig('userprivilege')
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

USER = 0
MASTER = 1
ADMIN = 2

class UserPrivilege(Entity):
	privilege = Field(Integer)
	user_id = Field(Integer)
	def __init__(self, privilege, user_id):
		self.privilege = privilege
		self.user_id = user_id

def isUser(user_id):
	try:
		priv = UserPrivilege.query.filter(UserPrivilege.user_id==user_id).filter(UserPrivilege.privilege==USER).one()
		return True
	except NoResultFound:
		return False


def isUserMaster(user_id):
	try:
		priv = UserPrivilege.query.filter(UserPrivilege.user_id==user_id).filter(UserPrivilege.privilege==MASTER).one()
		return True
	except NoResultFound:
		return False
		
def isUserAdmin(user_id):
	try:
		priv = UserPrivilege.query.filter(UserPrivilege.user_id==user_id).filter(UserPrivilege.privilege==ADMIN).one()
		return True
	except NoResultFound:
		return False

def isUserAtLeastMaster(user_id):
	return isUserMaster(user_id) or isUserAdmin(user_id)

def onSetMaster(cn, hash):
	if hash == sbserver.hashPassword(cn, sbserver.adminPassword()):
		sbserver.setAdmin(cn)

def onAuthSuccess(cn, name):
	sbserver.message(info(authtemp.substitute(colordict, name=sbserver.playerName(cn), authname=name)))

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
	registerServerEventHandler('player_setmaster', onSetMaster)
	registerServerEventHandler('player_setmaster_off', onSetMasterOff)
	registerServerEventHandler('player_claimed_master', onGainMaster)
	registerServerEventHandler('player_claimed_admin', onGainAdmin)
	registerServerEventHandler('player_released_master', onRelMaster)
	registerServerEventHandler('player_released_admin', onRelAdmin)
	registerServerEventHandler('player_auth_succeed', onAuthSuccess)

init()
