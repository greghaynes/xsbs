from xsbs.colors import red
from xsbs.ui import info, themedict
from xsbs.events import eventHandler
from xsbs.settings import loadPluginConfig
from xsbs.players import player
from xsbs.server import message as serverMessage

import string

config = {
	'Templates':
		{
			'teamkill': '${client_name}${tker}${text} team killed (${tkcount}) ${secondary_client_name}${victim}',
			'map_uploaded': '${client_name}${name}${text} uploaded a map. /getmap to receive it',
			'get_map': '${clent_name}${name}${text} is downloading the current map',
			'claim_master': '${client_name}${name}${text} claimed ${priv_master}Master',
			'claim_admin': '${client_name}${name}${text} claimed ${priv_admin}Admin',
			'relinquish_master': '${client_name}${name}${text} relinquished ${priv_master}Master',
			'relinquish_admin': '${client_name}${name}${text} relinquished ${priv_admin}Admin'
		}
	}

def init():
	loadPluginConfig(config, 'GameNotifications')
	for temp_name, temp_str in config['Templates'].items():
		config['Templates'][temp_name] = string.Template(temp_str)

@eventHandler('player_teamkill')
def teamkill_broadcast(cn, tcn):
	tker = player(cn)
	target = player(tcn)
	serverMessage(info(config['Templates']['teamkill'].substitute(themedict, tker=tker.name(), victim=target.name(), tkcount=tker.teamkills())))

@eventHandler('player_get_map')
def getmap(cn):
	p = player(cn)
	serverMessage(info(config['Templates']['get_map'].substitute(themedict, name=p.name())))

@eventHandler('player_uploaded_map')
def onUploadMap(cn):
	p = player(cn)
	serverMessage(info(config['Templates']['map_uploaded'].substitute(themedict, name=p.name())))

@eventHandler('player_claimed_master')
def onClaimMaster(cn):
	p = player(cn)
	serverMessage(info(config['Templates']['claim_master'].substitute(themedict, name=p.name())))

@eventHandler('player_claimed_admin')
def onClaimMaster(cn):
	p = player(cn)
	serverMessage(info(config['Templates']['claim_admin'].substitute(themedict, name=p.name())))

@eventHandler('player_relinquished_master')
def onClaimMaster(cn):
	p = player(cn)
	serverMessage(info(config['Templates']['relinquish_master'].substitute(themedict, name=p.name())))

@eventHandler('player_relinquished_admin')
def onClaimMaster(cn):
	p = player(cn)
	serverMessage(info(config['Templates']['relinquish_admin'].substitute(themedict, name=p.name())))

init()
