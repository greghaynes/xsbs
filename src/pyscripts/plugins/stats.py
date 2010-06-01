import string
from xsbs.commands import commandHandler
from xsbs.colors import colordict
from xsbs.settings import loadPluginConfig
from xsbs.ui import insufficientPermissions, error
from xsbs.players import player, isAtLeastMaster

config = {
	'Main':
		{
			'require_master': 'no',
		},
	'Templates':
		{
			'stats_message': '${white}Stats for ${orange}${name}\n${white}Frags: ${green}${frags} ${white}Deaths: ${red}${deaths} ${white}Teamkills: ${magenta}${teamkills} ${white}Accuracy: ${yellow}${accuracy}% ${white}KpD: ${orange}${ktd} ${white}Scores: ${blue}${score}'
		}
	}

def init():
	loadPluginConfig(config, 'Stats')
	config['Main']['require_master'] = config['Main']['require_master'] == 'yes'
	config['Templates']['stats_message'] = string.Template(config['Templates']['stats_message'])

@commandHandler('stats')
def onCommand(cp, args):
	'''@description Stats for the current match
	   @usage (cn)
	   @public'''
	if args != '':
		if require_master and not isPlayerMaster(cp.cn):
			insufficientPermissions(cp.cn)
			return
		try:
			p = player(int(args))
		except ValueError:
			cp.message(error('Usage: #stats (cn)'))
			return
	else:
		p = cp
	if not p.name():
		cp.message(error('You must use a valid cn'))
		return

	msg = template.substitute(colordict, name=p.name(), frags=p.frags(), deaths=p.deaths(), teamkills=p.teamkills(), shots=p.shots(), hits=p.hits(), accuracy=p.accuracy(), ktd=p.kpd(), score=p.score())
	cp.message(msg)
	
init()

