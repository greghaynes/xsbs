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
persistant_recording = config.getOption('Config', 'persistant_recording', 'off') == 'on'
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
	sbserver.setRecordNextMatch(persistant_recording)


@commandHandler('persistdemo')
@adminRequired
def setPersistantDemoRecord(cn, args):
	'''@description Enable/disable persistant demo recording
	   @usage on/off'''
	   
	global persistant_recording
	
	if args == 'on':
		player(cn).message(info('Enabling persistant demo recording'))
		persistant_recording = True
		sbserver.setRecordNextMatch(persistant_recording)
		
	elif args == 'off':
		player(cn).message(info('Disabling persistant demo recording'))
		persistant_recording = False
		sbserver.setRecordNextMatch(persistant_recording)
	else:
		raise UsageError('on/off')
