from xsbs.events import eventHandler
from xsbs.colors import colordict
from xsbs.ui import error, info
from xsbs.players import player, all as allPlayers, isAtLeastMaster
from xsbs.settings import loadPluginConfig
from xsbs.server import message as serverMessage
from xsbs.game import setMap

import sbserver
import logging
import string

config = {
	'Main':
		{
			'allow_mode_vote': 'no',
			'lock_game_mode': 'no',
		},
	'Templates':
		{
			'request_string': '${green}${user}${white} requested ${modename} on ${mapname}',
		}
	}

def init():
	loadPluginConfig(config, 'MapVote')
	config['Main']['allow_mode_vote'] = config['Main']['allow_mode_vote'] == 'yes'
	config['Main']['lock_game_mode'] = config['Main']['lock_game_mode'] == 'yes'
	config['Templates']['request_string'] = string.Template(config['Templates']['request_string'])

def vote(candidates, vote):
	for cand in candidates:
		if cand[0] == vote[0] and cand[1] == vote[1]:
			cand[2] += 1
			return cand[2]
	candidates.append([vote[0], vote[1], 1])
	return 1

def countVotes():
	players = allPlayers()
	votes_needed = (len(players) / 2)
	bestmap = ''
	bestmode = 0
	bestcount = 0
	candidates = []
	for p in allPlayers():
		try:
			pv = p.gamevars['mapvote']
			count = vote(candidates, pv)
			if count > bestcount:
				bestmap = pv[0]
				bestmode = pv[1]
				bestcount = count
		except (AttributeError, KeyError):
			pass
	if bestcount > votes_needed:
		serverMessage(info('Vote passed.'))
		setMap(bestmap, bestmode)

mapreload = [False]

@eventHandler('player_map_set')
def onMapSet(cn, mapname, mapmode):
	p = player(cn)
	if sbserver.mapName() == '':
		setMap(mapname, mapmode)
	elif mapreload[0]:
		setMap(mapname, mapmode)
		mapreload[0] = False
	elif isAtLeastMaster(cn) and sbserver.masterMode() > 0:
		sbserver.setMap(mapname, mapmode)
	elif mapmode != sbserver.gameMode() and (config['Main']['lock_game_mode'] or not config['Main']['allow_mode_vote']):
		p.message(error('You cannot request a new game mode'))

@eventHandler('player_map_vote')
def onMapVote(cn, mapname, mapmode):
	p = player(cn)
	if sbserver.mapName() == '':
		setMap(mapname, mapmode)
	elif isAtLeastMaster(cn) and sbserver.masterMode() > 0:
		setMap(mapname, mapmode)
	elif mapmode != sbserver.gameMode() and (config['Main']['lock_game_mode'] or not config['Main']['allow_mode_vote']):
		p.message(error('You cannot vote for a new game mode'))
	else:
		try:
			vote = player(cn).gamevars['mapvote']
			allow_vote = vote[0] != mapname and vote[1] != mapmode
		except KeyError:
			allow_vote = True
		if allow_vote:
			sbserver.message(info(config['Templates']['request_string'].substitute(colordict,
				user=p.name(),
				modename=sbserver.modeName(mapmode),
				mapname=mapname)))
			p.gamevars['mapvote'] = (mapname, mapmode)
		else:
			sbserver.playerMessage(cn, error('You have already requested this map.'))
	countVotes()

@eventHandler('reload_map_selection')
def onIntermEnd():
	mapreload[0] = True

init()
