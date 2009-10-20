from xsbs.events import registerServerEventHandler
from UserPrivelege.userpriv import masterRequired
import sbserver

def onSwitchTeam(cn, team):
	sbserver.setTeam(cn, team)

@masterRequired
def onSetTeam(cn, who, team):
	sbserver.setTeam(who, team)

registerServerEventHandler('player_switch_team', onSwitchTeam)
registerServerEventHandler('player_set_team', onSetTeam)

