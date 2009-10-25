import sbserver
import string, math
from xsbs.commands import registerCommandHandler
from xsbs.colors import colordict
from xsbs.settings import PluginConfig
from xsbs.ui import insufficientPermissions, error
from UserPrivilege.userpriv import isPlayerMaster

config = PluginConfig('stats')
template = config.getOption('Config', 'template', '${white}Stats for ${orange}${name}\n${white}Frags: ${green}${frags} ${white}Deaths: ${red}${deaths} ${white}Teamkills: ${magenta}${teamkills} ${white}Accuracy: ${yellow}${accuracy}% ${white}KpD: ${orange}${ktd}')
require_master = config.getOption('Config', 'require_master', 'no') == 'yes'
del config
template = string.Template(template)

def onCommand(cn, command):
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
	accuracy = 0
	if shots != 0:
		accuracy = hits / float(shots)
		accuracy = math.floor(accuracy * 100)
	if deaths == 0:
		ktd = frags
	else:
		ktd = frags / float(deaths)
		ktd *= float(100)
		ktd = math.floor(ktd)
		ktd = ktd / 100
	msg = template.substitute(colordict, name=name, frags=frags, deaths=deaths, teamkills=teamkills, shots=shots, hits=hits, accuracy=accuracy, ktd=ktd)
	sbserver.playerMessage(cn, msg)

registerCommandHandler('stats', onCommand)

