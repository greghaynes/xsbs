from xsbs.events import registerServerEventHandler, triggerServerEvent
from xsbs.settings import PluginConfig
from xsbs.game import modes
from xsbs.ui import error, info
from xsbs.colors import colordict
from xsbs.commands import registerCommandHandler
import logging
import sbserver
import string

config = PluginConfig('maprotation')
preset_rotation = config.getOption('Config', 'use_preset_rotation', 'yes') == 'yes'
start_mode = config.getOption('Config', 'start_mode', 'ffa')
nextmap_response = config.getOption('Config', 'nextmap_response', 'The next map is ${blue}${mapname}')
map_modes = config.getAllOptions('Maps')
del config
nextmap_response = string.Template(nextmap_response)

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

def onNextMapCmd(cn, args):
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #nextmap'))
	else:
		try:
			sbserver.playerMessage(cn, info(nextmap_response.substitute(colordict, mapname=getSuccessor(sbserver.gameMode(), sbserver.mapName()))))
		except (KeyError, ValueError):
			sbserver.playerMessage(cn, error('Could not determine next map'))

def onConnect(cn):
	if rotate_on_join[0]:
		sbserver.setPaused(False)

if preset_rotation:
	modeMapLists = {}
	for mode in map_modes:
		modeMapLists[mode[0]] = mode[1].replace(' ', '').split(',')
	rotate_on_join = [False]
	mn = modes.index(start_mode)
	sbserver.setMap(modeMapLists[start_mode][0], mn)
	registerServerEventHandler('intermission_ended', presetRotate)
	registerCommandHandler('nextmap', onNextMapCmd)
	registerServerEventHandler('player_connect', onConnect)
else:
	registerServerEventHandler('intermission_ended', onIntermEnd)

