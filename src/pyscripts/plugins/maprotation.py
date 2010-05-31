from xsbs.events import registerServerEventHandler, triggerServerEvent
from xsbs.settings import loadPluginConfig
from xsbs.game import modes
from xsbs.ui import error, info
from xsbs.colors import colordict
from xsbs.commands import registerCommandHandler
import logging
import sbserver
import string

config = {
	'Main':
		{
			'use_preset_rotation': 'yes',
			'start_mode': 'ffa',
		},
	'Templates':
		{
			'nextmap_response': 'The next map is ${blue}${mapname}',
		},
	'Maps':
		{
			'capture': 'urban_c, nevil_c, fb_capture, nmp9, c_valley, lostinspace, fc3, face-capture, nmp4, nmp8, hallo, monastery, ph-capture, hades, fc4, relic, frostbyte, venice, paradigm, corruption, asteroids, ogrosupply, reissen, akroseum, duomo, capture_night, c_egypt, tejen, dust2, campo, killcore3, damnation, arabic, cwcastle, river_c, serenity',
			'instactf': 'hallo, reissen, flagstone, face-capture, shipwreck, dust2, urban_c, berlin_wall, akroseum, valhalla, damnation, mach2, redemption, tejen, europium, capture_night, l_ctf, forge, campo, wdcd, sacrifice, core_transfer, recovery',
			'coop': 'complex, douze, ot, academy, metl2, metl3, nmp8, refuge, tartech, kalking1, dock, turbine, fanatic_quake, oddworld, wake5, aard3c, curvedm',
			'tacteam': 'complex, douze, ot, academy, metl2, metl3, nmp8, refuge, tartech, kalking1, dock, turbine, fanatic_quake, oddworld, wake5, aard3c, curvedm, fragplaza, pgdm, kffa, neondevastation, hog2, memento, neonpanic, lostinspace, DM_BS1, shindou, sdm1, shinmei1, stemple, powerplant, phosgene, oasis, island, metl4, ruby, frozen, ksauer1, killfactory, corruption, deathtek, aqueducts, orbe, roughinery, shadowed, torment, konkuri-to, moonlite, darkdeath, fanatic_castle_trap, orion, nmp10, katrez_d, thor, frostbyte, ogrosupply, kmap5, thetowers, guacamole, tejen, hades, paradigm, mechanic, wdcd',
			'demo': 'complex, douze, ot, academy, metl2, metl3, nmp8, refuge, tartech, kalking1, dock, turbine, fanatic_quake, oddworld, wake5, aard3c, curvedm',
			'tac': 'complex, douze, ot, academy, metl2, metl3, nmp8, refuge, tartech, kalking1, dock, turbine, fanatic_quake, oddworld, wake5, aard3c, curvedm, fragplaza, pgdm, kffa, neondevastation, hog2, memento, neonpanic, lostinspace, DM_BS1, shindou, sdm1, shinmei1, stemple, powerplant, phosgene, oasis, island, metl4, ruby, frozen, ksauer1, killfactory, corruption, deathtek, aqueducts, orbe, roughinery, shadowed, torment, konkuri-to, moonlite, darkdeath, fanatic_castle_trap, orion, nmp10, katrez_d, thor, frostbyte, ogrosupply, kmap5, thetowers, guacamole, tejen, hades, paradigm, mechanic, wdcd',
			'protect': 'hallo, reissen, flagstone, face-capture, shipwreck, dust2, urban_c, berlin_wall, akroseum, valhalla, damnation, mach2, redemption, tejen, europium, capture_night, l_ctf, forge, campo, wdcd, sacrifice, core_transfer, recovery',
			'instaprotect': 'hallo, reissen, flagstone, face-capture, shipwreck, dust2, urban_c, berlin_wall, akroseum, valhalla, damnation, mach2, redemption, tejen, europium, capture_night, l_ctf, forge, campo, wdcd, sacrifice, core_transfer, recovery',
			'ctf': 'hallo, reissen, flagstone, face-capture, shipwreck, dust2, urban_c, berlin_wall, akroseum, valhalla, damnation, mach2, redemption, tejen, europium, capture_night, l_ctf, forge, campo, wdcd, sacrifice, core_transfer, recovery',
			'insta': 'complex, douze, ot, academy, metl2, metl3, nmp8, refuge, tartech, kalking1, dock, turbine, fanatic_quake, oddworld, wake5, aard3c, curvedm, fragplaza, pgdm, kffa, neondevastation, hog2, memento, neonpanic, lostinspace, DM_BS1, shindou, sdm1, shinmei1, stemple, powerplant, phosgene, oasis, island, metl4, ruby, frozen, ksauer1, killfactory, corruption, deathtek, aqueducts, orbe, roughinery, shadowed, torment, konkuri-to, moonlite, darkdeath, fanatic_castle_trap, orion, nmp10, katrez_d, thor, frostbyte, ogrosupply, kmap5, thetowers, guacamole, tejen, hades, paradigm, mechanic, wdcd',
			'instateam': 'complex, douze, ot, academy, metl2, metl3, nmp8, refuge, tartech, kalking1, dock, turbine, fanatic_quake, oddworld, wake5, aard3c, curvedm, fragplaza, pgdm, kffa, neondevastation, hog2, memento, neonpanic, lostinspace, DM_BS1, shindou, sdm1, shinmei1, stemple, powerplant, phosgene, oasis, island, metl4, ruby, frozen, ksauer1, killfactory, corruption, deathtek, aqueducts, orbe, roughinery, shadowed, torment, konkuri-to, moonlite, darkdeath, fanatic_castle_trap, orion, nmp10, katrez_d, thor, frostbyte, ogrosupply, kmap5, thetowers, guacamole, tejen, hades, paradigm, mechanic, wdcd',
			'regencapture': 'urban_c, nevil_c, fb_capture, nmp9, c_valley, lostinspace, fc3, face-capture, nmp4, nmp8, hallo, monastery, ph-capture, hades, fc4, relic, frostbyte, venice, paradigm, corruption, asteroids, ogrosupply, reissen, akroseum, duomo, capture_night, c_egypt, tejen, dust2, campo, killcore3, damnation, arabic, cwcastle, river_c, serenity',
			'effic': 'complex, douze, ot, academy, metl2, metl3, nmp8, refuge, tartech, kalking1, dock, turbine, fanatic_quake, oddworld, wake5, aard3c, curvedm, fragplaza, pgdm, kffa, neondevastation, hog2, memento, neonpanic, lostinspace, DM_BS1, shindou, sdm1, shinmei1, stemple, powerplant, phosgene, oasis, island, metl4, ruby, frozen, ksauer1, killfactory, corruption, deathtek, aqueducts, orbe, roughinery, shadowed, torment, konkuri-to, moonlite, darkdeath, fanatic_castle_trap, orion, nmp10, katrez_d, thor, frostbyte, ogrosupply, kmap5, thetowers, guacamole, tejen, hades, paradigm, mechanic, wdcd',
			'teamplay': 'complex, douze, ot, academy, metl2, metl3, nmp8, refuge, tartech, kalking1, dock, turbine, fanatic_quake, oddworld, wake5, aard3c, curvedm, fragplaza, pgdm, kffa, neondevastation, hog2, memento, neonpanic, lostinspace, DM_BS1, shindou, sdm1, shinmei1, stemple, powerplant, phosgene, oasis, island, metl4, ruby, frozen, ksauer1, killfactory, corruption, deathtek, aqueducts, orbe, roughinery, shadowed, torment, konkuri-to, moonlite, darkdeath, fanatic_castle_trap, orion, nmp10, katrez_d, thor, frostbyte, ogrosupply, kmap5, thetowers, guacamole, tejen, hades, paradigm, mechanic, wdcd',
			'ffa': 'complex, douze, ot, academy, metl2, metl3, nmp8, refuge, tartech, kalking1, dock, turbine, fanatic_quake, oddworld, wake5, aard3c, curvedm, fragplaza, pgdm, kffa, neondevastation, hog2, memento, neonpanic, lostinspace, DM_BS1, shindou, sdm1, shinmei1, stemple, powerplant, phosgene, oasis, island, metl4, ruby, frozen, ksauer1, killfactory, corruption, deathtek, aqueducts, orbe, roughinery, shadowed, torment, konkuri-to, moonlite, darkdeath, fanatic_castle_trap, orion, nmp10, katrez_d, thor, frostbyte, ogrosupply, kmap5, thetowers, guacamole, tejen, hades, paradigm, mechanic, wdcd',
			'efficteam': 'complex, douze, ot, academy, metl2, metl3, nmp8, refuge, tartech, kalking1, dock, turbine, fanatic_quake, oddworld, wake5, aard3c, curvedm, fragplaza, pgdm, kffa, neondevastation, hog2, memento, neonpanic, lostinspace, DM_BS1, shindou, sdm1, shinmei1, stemple, powerplant, phosgene, oasis, island, metl4, ruby, frozen, ksauer1, killfactory, corruption, deathtek, aqueducts, orbe, roughinery, shadowed, torment, konkuri-to, moonlite, darkdeath, fanatic_castle_trap, orion, nmp10, katrez_d, thor, frostbyte, ogrosupply, kmap5, thetowers, guacamole, tejen, hades, paradigm, mechanic, wdcd',
		}
	}

def init():
	loadPluginConfig(config, 'MapRotation')
	config['Main']['use_preset_rotation'] = config['Main']['use_preset_rotation'] == 'yes'
	config['Templates']['nextmap_response'] = string.Template(config['Templates']['nextmap_response'])

init()

class Map:
	def __init__(self, name, mode):
		self.name = name
		self.mode = mode

def getSuccessor(mode_num, map):
	try:
		maps = modeMapLists[modes[mode_num]]
		if map == '':
			return maps[0]
		else:
			ndx = maps.index(map)
	except ValueError:
		if len(maps) > 0:
			logging.info('Current map not in rotation list.  Restarting rotation.')
			return maps[0]
		else:
			raise ValueError('Empty maps list for specfied mode')
	try:
	 	return maps[ndx+1]
	except IndexError:
		return maps[0]


def clientReloadRotate():
	triggerServerEvent('reload_map_selection', ())
	sbserver.sendMapReload()

def presetRotate():
	try:
		map = getSuccessor(sbserver.gameMode(), sbserver.mapName())
	except KeyError:
		logging.warning('No map list specified for current mode.  Defaulting to user-specified rotation.')
		clientReloadRotate()
	except ValueError:
		logging.info('Maps list for current mode is empty.  Defaulting to user-specified rotation.')
		clientReloadRotate()
	else:
		sbserver.setMap(map, sbserver.gameMode())
	if sbserver.numClients() == 0:
		rotate_on_join[0] = True
		sbserver.setPaused(True)

def onNextMapCmd(p, args):
	'''@description Display next map
	   @usage
	   @public'''
	if args != '':
		p.message(error('Usage: #nextmap'))
	else:
		try:
			p.messageinfo(config['Templates']['nextmap_response'].substitute(colordict, mapname=getSuccessor(sbserver.gameMode(), sbserver.mapName()))))
		except (KeyError, ValueError):
			sbserver.playerMessage(cn, error('Could not determine next map'))

def onConnect(cn):
	if rotate_on_join[0]:
		rotate_on_join[0] = False
		sbserver.setPaused(False)

if config['Main']['use_preset_rotation']:
	modeMapLists = {}
	for mode in config['Maps'].keys():
		modeMapLists[mode] = config['Maps'][mode].replace(' ', '').split(',')
	rotate_on_join = [False]
	mn = modes.index(config['Main']['start_mode'])
	sbserver.setMap(modeMapLists[config['Main']['start_mode']][0], mn)
	registerServerEventHandler('intermission_ended', presetRotate)
	registerCommandHandler('nextmap', onNextMapCmd)
	registerServerEventHandler('player_connect', onConnect)
else:
	registerServerEventHandler('intermission_ended', onIntermEnd)
	

