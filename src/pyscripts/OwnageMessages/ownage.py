import sbevents, sbserver, sbtools
import string

killsprees = {}
messages = { 5: string.Template(sbtools.green('$name') + ' is on a ' + sbtools.orange('KILLING SPREE!')),
	10: string.Template(sbtools.green('$name') + ' is ' + sbtools.orange('UNSTOPABLE!')),
	15: string.Template(sbtools.green('$name') + ' is ' + sbtools.orange('GODLIKE!')) }
endmsg = string.Template(sbtools.orange('$name') + '\'s killing spree ended by ' + sbtools.green('$endername'))

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

sbevents.registerEventHandler('player_active', onPlayerActive)
sbevents.registerEventHandler('player_frag', onPlayerFrag)
sbevents.registerEventHandler('player_teamkill', onPlayerTeamKill)

