import sbserver
import string, math
from xsbs.commands import commandHandler
from xsbs.colors import colordict
from xsbs.settings import PluginConfig
from xsbs.ui import insufficientPermissions, error
from xsbs.players import player, isAtLeastMaster

config = PluginConfig('stats')
template = config.getOption('Config', 'template', '${white}Stats for ${orange}${name}\n${white}Frags: ${green}${frags} ${white}Deaths: ${red}${deaths} ${white}Teamkills: ${magenta}${teamkills} ${white}Accuracy: ${yellow}${accuracy}% ${white}KpD: ${orange}${ktd}')
require_master = config.getOption('Config', 'require_master', 'no') == 'yes'
del config
template = string.Template(template)

@commandHandler('stats')
def onCommand(cn, command):
	'''@description Stats for the current match
	   @usage (cn)
	   @public'''
	if command != '':
		if require_master and not isPlayerMaster(cn):
			insufficientPermissions(cn)
			return
		try:
			tcn = int(command)
		except ValueError:
			sbserver.playerMessage(cn, error('Usage: #stats (cn)'))
			return
	else:
		tcn = cn
	name = sbserver.playerName(tcn)
	if not name:
		sbserver.playerMessage(cn, error('You must use a valid cn'))
		return
	frags = sbserver.playerFrags(tcn)
	deaths = sbserver.playerDeaths(tcn)
	teamkills = sbserver.playerTeamkills(tcn)
	shots = sbserver.playerShots(tcn)
	hits = sbserver.playerHits(tcn)
	accuracy = player(tcn).accuracy()
	ktd = player(tcn).kpd()
	msg = template.substitute(colordict, name=name, frags=frags, deaths=deaths, teamkills=teamkills, shots=shots, hits=hits, accuracy=accuracy, ktd=ktd)
	sbserver.playerMessage(cn, msg)

