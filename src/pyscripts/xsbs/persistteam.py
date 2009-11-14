from xsbs.events import eventHandler
from xsbs.commands import commandHandler
from xsbs.players import all as allPlayers
from xsbs.ui import error, notice
from UserPrivilege.userpriv import masterRequired
import sbserver

player_pteams = []

def onAutoteam():
	for p in player_pteams:
		sbserver.pregameSetTeam(p[0], p[1])

@commandHandler('persistteam')
@masterRequired
def persistentTeams(cn, args):
	if args == 'on':
		del player_pteams[:]
		for p in allPlayers():
			if p.team() != '':
				player_pteams.append((p.cn, p.team()))
		sbserver.message(notice('Persistent teams enabled'))
	elif args == 'off':
		del player_pteams[:]
		sbserver.message(notice('Persistent teams disabled'))
	else:
		player(cn).message(error('Usage: #persistentteams on/off'))

