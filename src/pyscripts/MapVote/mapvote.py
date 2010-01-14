from xsbs.events import eventHandler
from xsbs.colors import colordict
from xsbs.ui import error, info
from xsbs.players import player, all as allPlayers, isAtLeastMaster
from xsbs.settings import PluginConfig
import sbserver
import logging
import string

config = PluginConfig('mapvote')
allow_modevote = config.getOption('Config', 'allow_mode_vote', 'no') == 'yes'
lock_mode = config.getOption('Config', 'lock_game_mode', 'no') == 'yes'
request_temp = config.getOption('Config', 'request_string', '${green}${user}${white} requested ${modename} on ${mapname}')
del config
request_temp = string.Template(request_temp)

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
		sbserver.message(info('Vote passed.'))
		sbserver.setMap(bestmap, bestmode)

mapreload = [False]

@eventHandler('player_map_set')
def onMapSet(cn, mapname, mapmode):
	p = player(cn)
	if sbserver.mapName() == '':
		sbserver.setMap(mapname, mapmode)
	elif mapreload[0]:
		sbserver.setMap(mapname, mapmode)
		mapreload[0] = False
	elif isAtLeastMaster(cn) and sbserver.masterMode() > 0:
		sbserver.setMap(mapname, mapmode)
	elif mapmode != sbserver.gameMode() and (lock_mode or not allow_modevote):
		p.message(error('You cannot request a new game mode'))

@eventHandler('player_map_vote')
def onMapVote(cn, mapname, mapmode):
	p = player(cn)
	if sbserver.mapName() == '':
		sbserver.setMap(mapname, mapmode)
	elif isAtLeastMaster(cn) and sbserver.masterMode() > 0:
		sbserver.setMap(mapname, mapmode)
	elif mapmode != sbserver.gameMode() and (lock_mode or not allow_modevote):
		p.message(cn, error('You cannot vote for a new game mode'))
	else:
		try:
			vote = player(cn).gamevars['mapvote']
			allow_vote = vote[0] != mapname and vote[1] != mapmode
		except KeyError:
			allow_vote = True
		if allow_vote:
			sbserver.message(info(request_temp.substitute(colordict,
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

