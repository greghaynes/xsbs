from xsbs.events import eventHandler
from xsbs.players import player, all as allPlayers
from xsbs.settings import loadPluginConfig
from xsbs.colors import colordict
from xsbs.server import message as serverMessage

import string


config = {
	'Main':
		{
			'Multikill_awards': 'enabled',
		},
	'Templates':
		{
			'awards_prefix': '${blue}Awards: ${white}',
			'most_frags': 'Most Frags: ${orange}${name} ${blue}(${green}${count}${blue})${white} ',
			'most_teamkills': 'Most TeamKills: ${orange}${name} ${blue}(${green}${count}${blue})${white} ',
			'most_deaths': 'Most Deaths: ${orange}${name} ${blue}(${green}${count}${blue})${white} ',
			'most_accurate': 'Most Accurate: ${orange}${name} ${blue}(${green}${count}${blue})${white} ',

			'most_doublekills': 'Most Double Kills: ${orange}${name} ${blue}(${green}${count}${blue})${white} ',
			'most_triplekills': 'Most Triple Kills: ${orange}${name} ${blue}(${green}${count}${blue})${white} ',
			'most_overkills': 'Most Overkills: ${orange}${name} ${blue}(${green}${count}${blue})${white} ',
			'most_killtaculars': 'Most Killtacular: ${orange}${name} ${blue}(${green}${count}${blue})${white} ',
			'most_killotrocities': 'Most Killotrocities: ${orange}${name} ${blue}(${green}${count}${blue})${white} ',
			'most_killtastrophes': 'Most Killtastrophic: ${orange}${name} ${blue}(${green}${count}${blue})${white} ',
			'most_killapocalypses': 'Most Killapocalyptic: ${orange}${name} ${blue}(${green}${count}${blue})${white} ',
			'most_killionaires': 'Best Killionaire ${orange}${name} ${blue}(${green}${count}${blue})${white} ',
		}
	}


def init():
	loadPluginConfig(config, 'GameAwards')
	
	config['Templates']['awards_prefix'] = string.Template(config['Templates']['awards_prefix']).substitute(colordict)
	
	config['Templates']['most_frags'] = string.Template(config['Templates']['most_frags'])
	config['Templates']['most_teamkills'] = string.Template(config['Templates']['most_teamkills'])
	config['Templates']['most_deaths'] = string.Template(config['Templates']['most_deaths'])
	config['Templates']['most_accurate'] = string.Template(config['Templates']['most_accurate'])
	
	config['Main']['Multikill_awards'] = config['Main']['Multikill_awards'] == 'enabled'

	config['Templates']['most_doublekills'] = string.Template(config['Templates']['most_doublekills'])
	config['Templates']['most_triplekills'] = string.Template(config['Templates']['most_triplekills'])
	config['Templates']['most_overkills'] = string.Template(config['Templates']['most_overkills'])
	config['Templates']['most_killtaculars'] = string.Template(config['Templates']['most_killtaculars'])
	config['Templates']['most_killotrocities'] = string.Template(config['Templates']['most_killotrocities'])
	config['Templates']['most_killtastrophes'] = string.Template(config['Templates']['most_killtastrophes'])
	config['Templates']['most_killapocalypses'] = string.Template(config['Templates']['most_killapocalypses'])
	config['Templates']['most_killionaires'] = string.Template(config['Templates']['most_killionaires'])


@eventHandler('intermission_begin')
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

	if config['Main']['Multikill_awards']:
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
			
		if config['Main']['Multikill_awards']:
			try:
				try:
					doublekills	= p.ownagedata.multikill_counts[2]
				except KeyError:
					doublekills = 0
					
				try:
					triplekills = p.ownagedata.multikill_counts[3]
				except KeyError:
					triplekills = 0
					
				try:
					overkills = p.ownagedata.multikill_counts[5]
				except KeyError:
					overkills = 0
					
				try:
					killtaculars = p.ownagedata.multikill_counts[7]
				except KeyError:
					killtaculars = 0
					
				try:
					killotrocities	= p.ownagedata.multikill_counts[10]
				except KeyError:
					killotrocities = 0
					
				try:
					killtastrophes 	= p.ownagedata.multikill_counts[15]
				except KeyError:
					killtastrophes = 0
					
				try:
					killapocalypses	= p.ownagedata.multikill_counts[20]
				except KeyError:
					killapocalypses = 0
					
				try:
					killionaires = p.ownagedata.multikill_counts[25]
				except KeyError:
					killionaires = 0
				
				
				
				if config['Main']['Multikill_awards']:
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
		msg += config['Templates']['most_frags'].substitute(colordict, name=player(most_frags_cn).name(), count=most_frags)
		msg += ' '
	if most_tks > 0:
		msg += config['Templates']['most_teamkills'].substitute(colordict, name=player(most_tks_cn).name(), count=most_tks)
		msg += ' '
	if most_deaths > 0:
		msg += config['Templates']['most_deaths'].substitute(colordict, name=player(most_deaths_cn).name(), count=most_deaths)
		msg += ' '
	if most_accuracy > 0:
		msg += config['Templates']['most_accurate'].substitute(colordict, name=player(most_accurate_cn).name(), count=most_accuracy)

		
	if config['Main']['Multikill_awards']:
		if most_doublekills > 0:
			msg += config['Templates']['most_doublekills'].substitute(colordict, name=player(most_doublekills_cn).name(), count=most_doublekills)
			msg += ' '
		if most_triplekills > 0:
			msg += config['Templates']['most_triplekills'].substitute(colordict, name=player(most_triplekills_cn).name(), count=most_triplekills)
			msg += ' '
		if most_overkills > 0:
			msg += config['Templates']['most_overkills'].substitute(colordict, name=player(most_overkills_cn).name(), count=most_overkills)
			msg += ' '
		if most_killtaculars > 0:
			msg += config['Templates']['most_killtaculars'].substitute(colordict, name=player(most_killtaculars_cn).name(), count=most_killtaculars)
			msg += ' '
		if most_killotrocities > 0:
			msg += config['Templates']['most_killotrocities'].substitute(colordict, name=player(most_killotrocities_cn).name(), count=most_killotrocities)
			msg += ' '
		if most_killtastrophes > 0:
			msg += config['Templates']['most_killtastrophes'].substitute(colordict, name=player(most_killtastrophes_cn).name(), count=most_killtastrophes)
			msg += ' '
		if most_killapocalypses > 0:
			msg += config['Templates']['most_killapocalypses'].substitute(colordict, name=player(most_killapocalypses_cn).name(), count=most_killapocalypses)
			msg += ' '
		if most_killionaires > 0:
			msg += config['Templates']['most_killionaires'].substitute(colordict, name=player(most_killionaires_cn).name(), count=most_killionaires)
			msg += ' '
	
	if msg != '':
		msg = config['Templates']['awards_prefix'] + msg
		serverMessage(msg)
		
init()
