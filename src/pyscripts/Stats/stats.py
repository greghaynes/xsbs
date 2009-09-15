import sbserver
import string, math
from xsbs.commands import registerCommandHandler
from xsbs.colors import colordict
from xsbs.settings import PluginConfig

config = PluginConfig('stats')
template = config.getOption('Config', 'template', '${white}Stats for ${orange}${name}\n${white}Frags: ${green}${frags} ${white}Deaths: ${red}${deaths} ${white}Teamkills: ${magenta}${teamkills}')
template = string.Template(template)
del config

def onCommand(cn, command):
	if command != '':
		try:
			tcn = int(command)
		except ValueError:
			sbserver.playerMessage(cn, sbtools.red('Usage: #stats (cn)'))
			return
	else:
		tcn = cn
	name = sbserver.playerName(tcn)
	if not name:
		sbserver.playerMessage(cn, sbtools.red('You must use a valid cn'))
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
	msg = template.substitute(colordict, name=name, frags=frags, deaths=deaths, teamkills=teamkills, shots=shots, hits=hits, accuracy=accuracy)
	sbserver.playerMessage(cn, msg)

registerCommandHandler('stats', onCommand)

