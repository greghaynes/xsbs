import sbserver
from xsbs.settings import PluginConfig
from xsbs.colors import colordict
from xsbs.ui import notice
import string

config = PluginConfig('game')
pause_message = config.getOption(
	'Templates',
	'pause_message',
	'The game has been ${action} by ${orange}${name}')
del config
pause_message = string.Template(pause_message)

modes = [
	'ffa',
	'coop',
	'team',
	'insta',
	'instateam',
	'effic',
	'efficteam',
	'tac',
	'tacteam',
	'capture',
	'regencapture',
	'ctf',
	'instactf',
	'protect',
	'instaprotect'
]

def modeName(modenum):
	'''String representing game mode number'''
	return modes[modenum]

def modeNumber(modename):
	'''Number representing game mode string'''
	i = 0
	for mode in modes:
		if modename == mode:
			return i
		i += 1
	raise ValueError('Invalid mode')

def currentMap():
	'''Name of current map'''
	return sbserver.mapName()

def currentMode():
	'''Integer value of current game mode'''
	return sbserver.gameMode()

