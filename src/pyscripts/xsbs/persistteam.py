from xsbs.events import eventHandler
from xsbs.commands import commandHandler, UsageError
from xsbs.players import player, all as allPlayers
from xsbs.ui import error, notice
from xsbs.players import masterRequired
import sbserver

player_pteams = []

@eventHandler('autoteam')
def onAutoteam():
	for p in player_pteams:
		try:
			sbserver.pregameSetTeam(p[0], p[1])
		except ValueError:
			pass

@eventHandler('player_disconnect')
def onDisconnect(cn):
	i = 0
	for p in player_pteams:
		try:
			if p[0] == cn:
				del player_pteams[i]
				return
		except IndexError:
			pass
		i += 1

def persistentTeams(enabled):
	if enabled == True:
		del player_pteams[:]
		for p in allPlayers():
			try:
				if p.team() != '':
						player_pteams.append((p.cn, p.team()))
			except ValueError:
				pass
	elif enabled == False:
		del player_pteams[:]
	else:
		raise ValueError('Enabled must be boolean value')

@commandHandler('persistteam')
@masterRequired
def persistentTeamsCmd(cn, args):
	if args == 'on':
		persistentTeams(True)
		sbserver.message(notice('Persistent teams enabled'))
	elif args == 'off':
		persistentTeams(False)
		sbserver.message(notice('Persistent teams disabled'))
	else:
		raise UsageError('on/off')

