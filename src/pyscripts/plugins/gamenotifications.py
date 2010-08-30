from xsbs.colors import red
from xsbs.ui import info
from xsbs.colors import colordict
from xsbs.events import eventHandler
from xsbs.settings import loadPluginConfig
from xsbs.players import player
from xsbs.server import message as serverMessage

import string

config = {
	'Templates':
		{
			'teamkill': '${green}${tker}${white} team killed (${tkcount}) ${orange}${victim}',
			'map_uploaded': '${green}${name}${white} uploaded a map. /getmap to receive it',
			'get_map': '${green}${name}${white} is downloading map',
			'claim_master': '${green}${name}${white} claimed ${blue}Master',
			'claim_admin': '${green}${name}${white} claimed ${red}Admin',
			'relinquish_master': '${green}${name}${white} relinquished ${blue}Master',
			'relinquish_admin': '${green}${name}${white} relinquished ${red}Admin'
		}
	}

def init():
	loadPluginConfig(config, 'GameNotifications')
	config['Templates']['teamkill'] = string.Template(config['Templates']['teamkill'])
	config['Templates']['map_uploaded'] = string.Template(config['Templates']['map_uploaded'])
	config['Templates']['get_map'] = string.Template(config['Templates']['get_map'])
	config['Templates']['claim_master'] = string.Template(config['Templates']['claim_master'])
	config['Templates']['claim_admin'] = string.Template(config['Templates']['claim_admin'])
	config['Templates']['relinquish_master'] = string.Template(config['Templates']['relinquish_master'])
	config['Templates']['relinquish_admin'] = string.Template(config['Templates']['relinquish_admin'])

@eventHandler('player_teamkill')
def teamkill_broadcast(cn, tcn):
	tker = player(cn)
	target = player(tcn)
	serverMessage(info(config['Templates']['teamkill'].substitute(colordict, tker=tker.name(), victim=target.name(), tkcount=tker.teamkills())))

@eventHandler('player_get_map')
def getmap(cn):
	p = player(cn)
	serverMessage(info(config['Templates']['get_map'].substitute(colordict, name=p.name())))

@eventHandler('player_uploaded_map')
def onUploadMap(cn):
	p = player(cn)
	serverMessage(info(config['Templates']['map_uploaded'].substitute(colordict, name=p.name())))

@eventHandler('player_claimed_master')
def onClaimMaster(cn):
	p = player(cn)
	serverMessage(info(config['Templates']['claim_master'].substitute(colordict, name=p.name())))

@eventHandler('player_claimed_admin')
def onClaimMaster(cn):
	p = player(cn)
	serverMessage(info(config['Templates']['claim_admin'].substitute(colordict, name=p.name())))

@eventHandler('player_relinquished_master')
def onClaimMaster(cn):
	p = player(cn)
	serverMessage(info(config['Templates']['relinquish_master'].substitute(colordict, name=p.name())))

@eventHandler('player_relinquished_admin')
def onClaimMaster(cn):
	p = player(cn)
	serverMessage(info(config['Templates']['relinquish_admin'].substitute(colordict, name=p.name())))

init()
