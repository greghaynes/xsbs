from xsbs.events import eventHandler, execLater
from xsbs.players import isAtLeastMaster, player
from xsbs.ui import error, insufficientPermissions
from xsbs.game import currentMode
import sbserver

#modes where clients can swtich team
switchteam_modes = [
	4,
	6,
	8,
	10,
	11,
	12,
    14]

# modes where clients can set team name
setteam_modes = [
	2,
	4]

@eventHandler('player_switch_team')
def onSwitchTeam(cn, team):
	p = player(cn)
	mode = currentMode()
	if mode in setteam_modes:
		p.setTeam(team)
	elif mode in switchteam_modes:
		if team == 'good' or team == 'evil':
			p.setTeam(team)
		else:
			p.message(error('You cannot join specified team in current game mode.'))
	else:
		p.message(error('You can not set team in this game mode.'))

@eventHandler('player_set_team')
def onSetTeam(tcn, cn, team):
	p = player(cn)
	if cn != tcn and not isAtLeastMaster(tcn):
		insufficientPermissions(tcn)
		return
	mode = currentMode()
	if mode in setteam_modes:
		p.setTeam(team)
	elif mode in switchteam_modes:
		if team == 'good' or team == 'evil':
			p.setTeam(team)
		else:
			p.message(error('You cannot join specified team in current game mode.'))
	else:
		p.wessage(error('You can not set team in this game mode.'))

