from xsbs.events import registerServerEventHandler
import sbserver

def onSwitchTeam(cn, team):
	print 'switch team %s to %s', (sbserver.playerName(cn), team)

