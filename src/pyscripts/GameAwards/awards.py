from xsbs.events import registerServerEventHandler
from xsbs.players import player, all as allPlayers
from xsbs.settings import PluginConfig
from xsbs.colors import colordict
from xsbs.server import message as serverMessage

import string

config = PluginConfig('gameawards')
awards_prefix = config.getOption('Config', 'awards_prefix', '${blue}Awards: ${white}')
mftemp = config.getOption('Config', 'most_frags', 'Most Frags: ${orange}${name} ${blue}(${green}${count}${blue})${white} ')
mtktemp = config.getOption('Config', 'most_teamkills', 'Most TeamKills: ${orange}${name} ${blue}(${green}${count}${blue})${white} ')
mdtemp = config.getOption('Config', 'most_deaths', 'Most Deaths: ${orange}${name} ${blue}(${green}${count}${blue})${white} ')
matemp = config.getOption('Config', 'most_accurate', 'Most Accurate: ${orange}${name} ${blue}(${green}${count}${blue})${white} ')
del config
awards_prefix = string.Template(awards_prefix).substitute(colordict)
mftemp = string.Template(mftemp)
mtktemp = string.Template(mtktemp)
mdtemp = string.Template(mdtemp)
matemp = string.Template(matemp)

def onIntermission():
	players = allPlayers()
	most_frags = 0
	most_frags_cn = 0
	most_tks = 0
	most_tks_cn = -1
	most_deaths = 0
	most_deaths_cn = -1
	most_accuracy = 0
	most_accurate_cn = -1

	for p in players:
		try:
			frags = p.frags()
			teamkills = p.teamkills()
			deaths = p.deaths()
			accuracy = p.accuracy()
			if frags > most_frags or most_frags_cn == -1:
				most_frags = frags
				most_frags_cn = p.cn
			if teamkills > most_tks or most_tks_cn == -1:
				most_tks = teamkills
				most_tks_cn = p.cn
			if deaths > most_deaths or most_deaths_cn == -1:
				most_deaths = deaths
				most_deaths_cn = p.cn
			if accuracy > most_accuracy or most_accurate_cn == -1:
				most_accuracy = accuracy
				most_accurate_cn = p.cn
		except ValueError:
			continue
	msg = ''
	if most_frags > 0:
		msg += mftemp.substitute(colordict, name=player(most_frags_cn).name(), count=most_frags)
		msg += ' '
	if most_tks > 0:
		msg += mtktemp.substitute(colordict, name=player(most_tks_cn).name(), count=most_tks)
		msg += ' '
	if most_deaths > 0:
		msg += mdtemp.substitute(colordict, name=player(most_deaths_cn).name(), count=most_deaths)
		msg += ' '
	if most_accuracy > 0:
		msg += matemp.substitute(colordict, name=player(most_accurate_cn).name(), count=most_accuracy)
	if msg != '':
		msg = awards_prefix + msg
		serverMessage(msg)

registerServerEventHandler('intermission_begin', onIntermission)

