from xsbs.events import eventHandler
from xsbs.commands import commandHandler
from xsbs.players import player, all as allPlayers
from xsbs.ui import error, notice
from UserPrivilege.userpriv import masterRequired
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
		if p[i] == cn:
			del p[i]
			return
		i += 1

@commandHandler('persistteam')
@masterRequired
def persistentTeams(cn, args):
	if args == 'on':
		del player_pteams[:]
		for p in allPlayers():
			try:
				if p.team() != '':
						player_pteams.append((p.cn, p.team()))
			except ValueError:
				pass
		sbserver.message(notice('Persistent teams enabled'))
	elif args == 'off':
		del player_pteams[:]
		sbserver.message(notice('Persistent teams disabled'))
	else:
		player(cn).message(error('Usage: #persistentteams on/off'))

