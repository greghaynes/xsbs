import sbserver
from xsbs.colors import green, orange
from xsbs.events import registerServerEventHandler
import string

killsprees = {}
messages = { 5: string.Template(green('$name') + ' is on a ' + orange('KILLING SPREE!')),
	10: string.Template(green('$name') + ' is ' + orange('UNSTOPABLE!')),
	15: string.Template(green('$name') + ' is ' + orange('GODLIKE!')) }
endmsg = string.Template(orange('$name') + '\'s killing spree ended by ' + green('$endername'))

def onPlayerActive(cn):
	killsprees[cn] = 0

def onPlayerFrag(cn, tcn):
	if cn not in sbserver.players():
		print 'player_frag event has lost its marbles: cn is %i' % cn
	killsprees[cn] = killsprees[cn] + 1
	if killsprees[tcn] > 5:
		sbserver.message(endmsg.substitute(name=sbserver.playerName(tcn), endername=sbserver.playerName(cn)))
	killsprees[tcn] = 0
	if messages.has_key(killsprees[cn]):
		sbserver.message(messages[killsprees[cn]].substitute(name=sbserver.playerName(cn)))

def onPlayerTeamKill(cn, tcn):
	killsprees[cn] = 0

registerServerEventHandler('player_active', onPlayerActive)
registerServerEventHandler('player_frag', onPlayerFrag)
registerServerEventHandler('player_teamkill', onPlayerTeamKill)

