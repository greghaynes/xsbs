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
			'gain_master': '${green}${name}${white} claimed ${red}master',
			'gain_admin': '${green}${name}${white} claimed ${red}admin',
			'release_master': '${green}${name}${white} relinquished ${red}master',
			'release_admin': '${green}${name}${white} relinquished ${red}admin',
		}
	}

USER = 0
MASTER = 1
ADMIN = 2

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
	config['Templates']['gain_master'] = string.Template(config['Templates']['gain_master'])
	config['Templates']['gain_admin'] = string.Template(config['Templates']['gain_admin'])
	config['Templates']['release_master'] = string.Template(config['Templates']['release_master'])
	config['Templates']['release_admin'] = string.Template(config['Templates']['release_admin'])
	
	registerServerEventHandler('player_setmaster_off', onSetMasterOff)
	registerServerEventHandler('player_claimed_master', onGainMaster)
	registerServerEventHandler('player_claimed_admin', onGainAdmin)
	registerServerEventHandler('player_released_master', onRelMaster)
	registerServerEventHandler('player_released_admin', onRelAdmin)

init()
