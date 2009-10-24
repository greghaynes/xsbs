from xsbs.events import registerServerEventHandler
from xsbs.ui import error, info
from xsbs.players import player, all as allPlayers
from xsbs.settings import PluginConfig
from UserPrivilege.userpriv import isPlayerMaster
import sbserver

config = PluginConfig('mapvote')
allow_modevote = config.getOption('Config', 'allow_mode_vote', 'no') == 'yes'
lock_mode = config.getOption('Config', 'lock_game_mode', 'no') == 'yes'
del config

def vote(candidates, vote):
	for cand in candidates:
		if cand[0] == vote[0] and cand[1] == vote[1]:
			cand[2] += 1
			return cand[2]
	candidates.append((vote[0], vote[1], 1))
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

def onMapSet(cn, mapname, mapmode):
	if sbserver.mapName() == '':
		sbserver.setMap(mapname, mapmode)
	elif mapreload[0]:
		sbserver.setMap(mapname, mapmode)
		mapreload[0] = False
	elif (sbserver.playerPrivilege(cn) > 0 or isPlayerMaster(cn)) and sbserver.masterMode() > 0:
		sbserver.setMap(mapname, mapmode)
	elif mapmode != sbserver.gameMode() and (lock_mode or (not allow_modevote and sbserver.playerPrivilege(cn) == 0)):
		sbserver.playerMessage(cn, error('You cannot request a new game mode'))

def onMapVote(cn, mapname, mapmode):
	if sbserver.mapName() == '':
		sbserver.setMap(mapname, mapmode)
	elif (sbserver.playerPrivilege(cn) > 0 or isPlayerMaster(cn)) and sbserver.masterMode() > 0:
		sbserver.setMap(mapname, mapmode)
	elif mapmode != sbserver.gameMode() and (lock_mode or (not allow_modevote and sbserver.playerPrivilege(cn) == 0)):
		sbserver.playerMessage(cn, error('You cannot request a new game mode'))
	else:
		try:
			vote = player(cn).gamevars['mapvote']
			allow_vote = vote[0] != mapname and vote[1] != mapmode
		except KeyError:
			allow_vote = True
		if allow_vote:
			sbserver.message(info('%s requested %s on %s' % (sbserver.playerName(cn), sbserver.modeName(mapmode), mapname)))
			player(cn).gamevars['mapvote'] = (mapname, mapmode)
		else:
			sbserver.playerMessage(cn, error('You have already requested this map.'))
	countVotes()

def onIntermEnd():
	mapreload[0] = True

registerServerEventHandler('player_map_set', onMapSet)
registerServerEventHandler('player_map_vote', onMapVote)
registerServerEventHandler('reload_map_selection', onIntermEnd)

