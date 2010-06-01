import sbserver

from elixir import Entity, Field, String, Integer, Boolean, ManyToOne, OneToMany, setup_all, session
from sqlalchemy.orm.exc import NoResultFound

from xsbs.events import registerServerEventHandler
from xsbs.ui import error, info, insufficientPermissions
from xsbs.colors import colordict
from xsbs.settings import loadPluginConfig
import string

config = {
	'Templates':
		{
			'authenticated': '${green}${name}${white} authenticated as ${magenta}${authname}',
			'gain_master': '${green}${name}${white} claimed ${red}master',
			'gain_admin': '${green}${name}${white} claimed ${red}admin',
			'release_master': '${green}${name}${white} relinquished ${red}master',
			'release_admin': '${green}${name}${white} relinquished ${red}admin',
		}
	}

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
	sbserver.message(info(config['Templates']['authenticated'].substitute(colordict, name=sbserver.playerName(cn), authname=name)))

def onSetMasterOff(cn):
	sbserver.resetPrivilege(cn)

def onGainMaster(cn):
	sbserver.message(info(config['Templates']['gain_master'].substitute(colordict, name=sbserver.playerName(cn))))

def onGainAdmin(cn):
	sbserver.message(info(config['Templates']['gain_admin'].substitute(colordict, name=sbserver.playerName(cn))))

def onRelMaster(cn):
	sbserver.message(info(config['Templates']['release_master'].substitute(colordict, name=sbserver.playerName(cn))))

def onRelAdmin(cn):
	sbserver.message(info(config['Templates']['release_admin'].substitute(colordict, name=sbserver.playerName(cn))))

def init():
	loadPluginConfig(config, 'UserPrivilege')
	config['Templates']['authenticated'] = string.Template(config['Templates']['authenticated'])
	config['Templates']['gain_master'] = string.Template(config['Templates']['gain_master'])
	config['Templates']['gain_admin'] = string.Template(config['Templates']['gain_admin'])
	config['Templates']['release_master'] = string.Template(config['Templates']['release_master'])
	config['Templates']['release_admin'] = string.Template(config['Templates']['release_admin'])
	
	registerServerEventHandler('player_setmaster', onSetMaster)
	registerServerEventHandler('player_setmaster_off', onSetMasterOff)
	registerServerEventHandler('player_claimed_master', onGainMaster)
	registerServerEventHandler('player_claimed_admin', onGainAdmin)
	registerServerEventHandler('player_released_master', onRelMaster)
	registerServerEventHandler('player_released_admin', onRelAdmin)
	registerServerEventHandler('player_auth_succeed', onAuthSuccess)

init()
