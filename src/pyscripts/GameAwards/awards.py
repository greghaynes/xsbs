from xsbs.events import registerServerEventHandler
from xsbs.players import all as allPlayers
from xsbs.settings import PluginConfig
from xsbs.colors import colordict
import sbserver
import string

config = PluginConfig('gameawards')
awards_prefix = config.getOption('Config', 'awards_prefix', '${blue}Awards: ${white}')
mftemp = config.getOption('Config', 'most_frags', 'Most Frags: ${orange}${name} (${green}${count}${white})')
mtktemp = config.getOption('Config', 'most_teamkills', 'Most TeamKills: ${orange}${name} (${green}${count}${white})')
del config
awards_prefix = string.Template(awards_prefix).substitute(colordict)
mftemp = string.Template(mftemp)

def onIntermission():
	players = allPlayers()
	most_frags = 0
	most_frags_cn = 0
	most_tks = 0
	most_tks_cn = -1
	for player in players:
		try:
			frags = sbserver.playerFrags(player.cn)
			teamkills = sbserver.playerTeamkills(player.cn)
			if frags > most_frags or most_frags_cn == -1:
				most_frags = sbserver.playerFrags(player.cn)
				most_frags_cn = player.cn
			if teamkills > most_tks or most_tks_cn == -1:
				most_tks = sbserver.playerTeamkills(player.cn)
				most_tks_cn = player.cn
		except ValueError:
			continue
	msg = ''
	if most_frags > 0:
		msg += mftemp.substitute(colordict, name=sbserver.playerName(most_frags_cn), count=most_frags)
		msg += ' '
	if most_tks > 0:
		msg += mtktemp.substitute(colordict, name=sbserver.playerName(most_tks_cn), count=most_tks)
		msg += ' '
	if msg != '':
		msg = awards_prefix + msg
		sbserver.message(msg)

registerServerEventHandler('intermission_begin', onIntermission)

