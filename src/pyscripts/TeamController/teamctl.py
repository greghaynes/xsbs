from xsbs.events import eventHandler
from UserPrivilege.userpriv import masterRequired
from xsbs.ui import error
import sbserver

switchteam_modes = [
	4,
	6,
	8,
	10,
	11,
	12]

setteam_modes = [
	2,
	4]

@eventHandler('player_switch_team')
def onSwitchTeam(cn, team):
	mode =  sbserver.gameMode()
	if mode in setteam_modes:
		sbserver.setTeam(cn, team)
	elif mode in switchteam_modes:
		if team == 'good' or team == 'evil':
			sbserver.setTeam(cn, team)
		else:
			sbserver.playerMessage(cn, error('You cannot join specified team in current game mode.'))
	else:
		sbserver.playerMessage(cn, error('You can not set team in this game mode.'))

@eventHandler('player_set_team')
@masterRequired
def onSetTeam(cn, who, team):
	mode =  sbserver.gameMode()
	if mode in setteam_modes or team == 'evil' or team == 'good':
		sbserver.setTeam(who, team)
	else:
		sbserver.playerMessage(cn, error('You can not set team in this game mode.'))

