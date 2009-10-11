from xsbs.events import registerServerEventHandler, triggerServerEvent
from xsbs.settings import PluginConfig
from xsbs.game import modes
import logging
import sbserver

config = PluginConfig('maprotation')
preset_rotation = config.getOption('Config', 'use_preset_rotation', 'yes') == 'yes'
start_mode = config.getOption('Config', 'start_mode', 'ffa')
map_modes = config.getAllOptions('Maps')
del config

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

if preset_rotation:
	modeMapLists = {}
	for mode in map_modes:
		modeMapLists[mode[0]] = mode[1].replace(' ', '').split(',')
	presetRotate()

if preset_rotation:
	registerServerEventHandler('intermission_ended', presetRotate)
else:
	registerServerEventHandler('intermission_ended', onIntermEnd)

