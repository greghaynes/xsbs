import sbserver
from xsbs.commands import commandHandler, UsageError
from xsbs.events import eventHandler
from xsbs.ui import info, notice
from xsbs.settings import PluginConfig
from xsbs.colors import colordict
from xsbs.players import player, masterRequired, adminRequired
import string

config = PluginConfig('demorecord')
action_temp = config.getOption('Config', 'record_next_message', 'Demo recording is ${action} for next match (by ${orange}${user}${white}${white}${white}${white})')
persistent_recording = config.getOption('Config', 'persistent_recording', 'no') == 'yes'
del config
action_temp = string.Template(action_temp)

@eventHandler('player_record_demo')
@masterRequired
def playerRecordNextMatch(cn, val):
	if val == sbserver.nextMatchRecorded():
		return
	if val:
		act = 'enabled'
	else:
		act = 'disabled'
	sbserver.setRecordNextMatch(val)
	sbserver.message(notice(action_temp.substitute(colordict, action=act, user=sbserver.playerName(cn))))

@eventHandler('map_changed')
def persistRecordNextMatch(themap, themode):
	sbserver.setRecordNextMatch(persistent_recording)

@commandHandler('persistdemo')
@adminRequired
def setPersistantDemoRecord(cn, args):
	'''@description Enable/disable persistant demo recording
	   @usage enable/disable'''
	if args == 'enable':
		player(cn).message(info('Enabling persistant demo recording'))
		persistent_recording = True
		sbserver.setRecordNextMatch(persistent_recording)
		
	elif args == 'disable':
		player(cn).message(info('Disabling persistant demo recording'))
		persistent_recording = False
		sbserver.setRecordNextMatch(persistent_recording)
	else:
		raise UsageError()

