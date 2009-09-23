import sbserver
from xsbs.colors import green, orange
from xsbs.events import registerServerEventHandler
from xsbs.players import player
import string

messages = { 5: string.Template(green('$name') + ' is on a ' + orange('KILLING SPREE!')),
	10: string.Template(green('$name') + ' is ' + orange('UNSTOPABLE!')),
	15: string.Template(green('$name') + ' is ' + orange('GODLIKE!')) }
endmsg = string.Template(orange('$name') + '\'s killing spree ended by ' + green('$endername'))

def onPlayerFrag(cn, tcn):
	try:
		p = player(cn)
		t = player(tcn)
	except ValueError:
		pass
	if cn == tcn:
		p.killspree = 0
	else:
		try:
			p.killspree += 1
		except AttributeError:
			p.killspree = 1
		try:
			if t.killspree >= 5:
				sbserver.message(endmsg.substitute(name=sbserver.playerName(tcn), endername=sbserver.playerName(cn)))
			t.killspree = 0
		except AttributeError:
			t.killspree = 0
		try:
			sbserver.message(messages[p.killspree].substitute(name=sbserver.playerName(cn)))
		except KeyError:
			pass

def onPlayerTeamKill(cn, tcn):
	player(cn).killspree = 0

registerServerEventHandler('player_frag', onPlayerFrag)
registerServerEventHandler('player_teamkill', onPlayerTeamKill)

