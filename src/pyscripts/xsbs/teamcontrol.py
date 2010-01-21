from xsbs.events import eventHandler, execLater
from xsbs.players import isAtLeastMaster, player
from xsbs.ui import error, insufficientPermissions
from xsbs.game import currentMode, modeName
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

def isSafeTeam(team):
	'''Is team safe based on current mode.
	   ex: isSafeTeam('test') would return false in capture mode.'''
	mode = currentMode()
	if mode in setteam_modes:
		return True
	if mode in switchteam_modes and team in ['good', 'evil']:
		return True
	return False

@eventHandler('player_switch_team')
def onSwitchTeam(cn, team):
	p = player(cn)
	if isSafeTeam(team):
		execLater(p.suicide())
		p.setTeam(team)
	else:
		p.message(error('You cannot join team \'%s\' in game mode %s' % (
				team,
				modeName(currentMode())
				)))

@eventHandler('player_set_team')
def onSetTeam(tcn, cn, team):
	p = player(cn)
	r = player(tcn)
	if cn != tcn and not isAtLeastMaster(tcn):
		insufficientPermissions(tcn)
		return
	mode = currentMode()
	if isSafeTeam(team):
		execLater(p.suicide())
		p.setTeam(team)
	else:
		r.message(error('You cannot join team \'%s\' in game mode %s' % (
				team,
				modeName(currentMode())
				)))

