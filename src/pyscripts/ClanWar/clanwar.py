from xsbs.events import eventHandler
from xsbs.ui import error
from xsbs.player import player, all as allPlayers
from UserPrivilege.userprivilege import masterRequired
import sbserver
import re

@eventHandler('clanwar')
@masterRequired
def clanWar(cn, args):
	clans = args.split(' ')
	if len(clans) != 2:
		player(cn).message(error('Usage: #clanwar <clan1> <clan2>'))
	else:
		c1r = re.compile('^' + clans[0])
		c2r = re.compile('^' + clans[1])
		sbserver.pause()
		for p in allPlayers():
			if c1r.match(p.name()):
				p.setTeam('good')
			else if c2r.match(p.name()):
				p.setTeam('evil')
			else:
				p.spectate()

