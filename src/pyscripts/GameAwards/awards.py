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

newawards_enabled = config.getOption('Config', 'Multikill_awards', 'enabled') == 'enabled'
most_doublekillstemp = config.getOption('Config', 'most_doublekills', 'Most Double Kills: ${orange}${name} ${blue}(${green}${count}${blue})${white} ')
most_triplekillstemp = config.getOption('Config', 'most_triplekills', 'Most Triple Kills: ${orange}${name} ${blue}(${green}${count}${blue})${white} ')
most_overkillstemp = config.getOption('Config', 'most_overkills', 'Most Overkills: ${orange}${name} ${blue}(${green}${count}${blue})${white} ')
most_killtacularstemp = config.getOption('Config', 'most_killtaculars', 'Most Killtacular: ${orange}${name} ${blue}(${green}${count}${blue})${white} ')
most_killotrocitiestemp = config.getOption('Config', 'most_killotrocities', 'Most Killotrocities: ${orange}${name} ${blue}(${green}${count}${blue})${white} ')
most_killtastrophestemp = config.getOption('Config', 'most_killtastrophes', 'Most Killtastrophic: ${orange}${name} ${blue}(${green}${count}${blue})${white} ')
most_killapocalypsestemp = config.getOption('Config', 'most_killapocalypses', 'Most Killapocalyptic: ${orange}${name} ${blue}(${green}${count}${blue})${white} ')
most_killionairestemp = config.getOption('Config', 'most_killionaires', 'Best Killionaire ${orange}${name} ${blue}(${green}${count}${blue})${white} ')



del config
awards_prefix = string.Template(awards_prefix).substitute(colordict)
mftemp = string.Template(mftemp)
mtktemp = string.Template(mtktemp)
mdtemp = string.Template(mdtemp)
matemp = string.Template(matemp)

most_doublekillstemp = string.Template(most_doublekillstemp)
most_triplekillstemp = string.Template(most_triplekillstemp)
most_overkillstemp = string.Template(most_overkillstemp)
most_killtacularstemp = string.Template(most_killtacularstemp)
most_killotrocitiestemp = string.Template(most_killotrocitiestemp)
most_killtastrophestemp = string.Template(most_killtastrophestemp)
most_killapocalypsestemp = string.Template(most_killapocalypsestemp)
most_killionairestemp = string.Template(most_killionairestemp)


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

	if newawards_enabled:
		most_doublekills = 0
		most_doublekills_cn = -1
		most_triplekills = 0
		most_triplekills_cn = -1
		most_overkills = 0
		most_overkills_cn = -1
		most_killtaculars = 0
		most_killtaculars_cn = -1
		most_killotrocities = 0
		most_killotrocities_cn = -1
		most_killtastrophes = 0
		most_killtastrophes_cn = -1
		most_killapocalypses = 0
		most_killapocalypses_cn = -1
		most_killionaires = 0
		most_killionaires_cn = -1
	
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
			
		if newawards_enabled:
			try:
				try:
					doublekills	= p.ownagedata.multikill_counts[2]
				except:
					doublekills = 0
					
				try:
					triplekills = p.ownagedata.multikill_counts[3]
				except:
					triplekills = 0
					
				try:
					overkills = p.ownagedata.multikill_counts[5]
				except:
					overkills = 0
					
				try:
					killtaculars = p.ownagedata.multikill_counts[7]
				except:
					killtaculars = 0
					
				try:
					killotrocities	= p.ownagedata.multikill_counts[10]
				except:
					killotrocities = 0
					
				try:
					killtastrophes 	= p.ownagedata.multikill_counts[15]
				except:
					killtastrophes = 0
					
				try:
					killapocalypses	= p.ownagedata.multikill_counts[20]
				except:
					killapocalypses = 0
					
				try:
					killionaires = p.ownagedata.multikill_counts[25]
				except:
					killionaires = 0
				
				
				
				if doublekills > most_doublekills or most_doublekills_cn == -1:
					most_doublekills = doublekills
					most_doublekills_cn = p.cn
				if triplekills > most_triplekills or most_triplekills_cn == -1:
					most_triplekills = triplekills
					most_triplekills_cn = p.cn
				if overkills > most_overkills or most_overkills_cn == -1:
					most_overkills = overkills
					most_overkills_cn = p.cn
				if killtaculars > most_killtaculars or most_killtaculars_cn == -1:
					most_killtaculars = killtaculars
					most_killtaculars_cn = p.cn
				if killotrocities > most_killotrocities or most_killotrocities_cn == -1:
					most_killotrocities = killotrocities
					most_killotrocities_cn = p.cn
				if killtastrophes > most_killtastrophes or most_killtastrophes_cn == -1:
					most_killtastrophes = killtastrophes
					most_killtastrophes_cn = p.cn
				if killapocalypses > most_killapocalypses or most_killapocalypses_cn == -1:
					most_killapocalypses = killapocalypses
					most_killapocalypses_cn = p.cn
				if killionaires > most_killionaires or most_killionaires_cn == -1:
					most_killionaires = killionaires
					most_killionaires_cn = p.cn
			except (KeyError, ValueError):
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

		
	if newawards_enabled:
		if most_doublekills > 0:
			msg += most_doublekillstemp.substitute(colordict, name=player(most_doublekills_cn).name(), count=most_doublekills)
			msg += ' '
		if most_triplekills > 0:
			msg += most_triplekillstemp.substitute(colordict, name=player(most_triplekills_cn).name(), count=most_triplekills)
			msg += ' '
		if most_overkills > 0:
			msg += most_overkillstemp.substitute(colordict, name=player(most_overkills_cn).name(), count=most_overkills)
			msg += ' '
		if most_killtaculars > 0:
			msg += most_killtacularstemp.substitute(colordict, name=player(most_killtaculars_cn).name(), count=most_killtaculars)
			msg += ' '
		if most_killotrocities > 0:
			msg += most_killotrocitiestemp.substitute(colordict, name=player(most_killotrocities_cn).name(), count=most_killotrocities)
			msg += ' '
		if most_killtastrophes > 0:
			msg += most_killtastrophestemp.substitute(colordict, name=player(most_killtastrophes_cn).name(), count=most_killtastrophes)
			msg += ' '
		if most_killapocalypses > 0:
			msg += most_killapocalypsestemp.substitute(colordict, name=player(most_killapocalypses_cn).name(), count=most_killapocalypses)
			msg += ' '
		if most_killionaires > 0:
			msg += most_killionairestemp.substitute(colordict, name=player(most_killionaires_cn).name(), count=most_killionaires)
			msg += ' '
	
	if msg != '':
		msg = awards_prefix + msg
		serverMessage(msg)

registerServerEventHandler('intermission_begin', onIntermission)

