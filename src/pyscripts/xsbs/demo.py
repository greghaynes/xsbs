import sbserver
from xsbs.commands import commandHandler, UsageError
from xsbs.events import eventHandler
from xsbs.ui import info, notice
from xsbs.settings import PluginConfig
from xsbs.colors import colordict
from xsbs.players import player, masterRequired, adminRequired, isUserAdmin, isUserAtLeastMaster
from xsbs.ui import insufficientPermissions
import string
import logging

config = PluginConfig('demorecord')
action_temp = config.getOption('Config', 'record_next_message', 'Demo recording is ${action} for next match (by ${orange}${user}${white}${white}${white}${white})')
persistent_recording = config.getOption('Config', 'persistent_recording', 'no') == 'yes'
required_permissions = config.getOption('Config', 'required_permissions', 'master')
del config
action_temp = string.Template(action_temp)
if required_permissions == 'user':
	required_permissions = 0
elif required_permissions == 'master':
	required_permissions = 1
elif required_permissions == 'admin':
	required_permissions = 2
else:
	logging.error('invalid required_permissions')
	required_permissions = 1

def permissions_ok(cn):
	if required_permissions == 0:
		return True
	p = player(cn)
	if required_permissions == 1:
		return p.isAtLeastMaster()
	if required_permissions == 2:
		return p.isAdmin()
	logging.error('required_permissions not an int!')
	return False
	

@eventHandler('player_record_demo')
def playerRecordNextMatch(p, val):
	if permissions_ok(p.cn):
		if val == sbserver.nextMatchRecorded():
			return
		if val:
			act = 'enabled'
		else:
			act = 'disabled'
		sbserver.setRecordNextMatch(val)
		sbserver.message(notice(action_temp.substitute(colordict, action=act, user=p.name())))
	else:
		insufficientPermissions(p.cn)

@eventHandler('map_changed')
def persistRecordNextMatch(themap, themode):
	sbserver.setRecordNextMatch(persistent_recording)

@commandHandler('persistdemo')
@adminRequired
def setPersistantDemoRecord(p, args):
	'''@description Enable/disable persistant demo recording
	   @usage enable/disable'''
	if args == 'enable':
		p.message(info('Enabling persistant demo recording'))
		persistent_recording = True
		sbserver.setRecordNextMatch(persistent_recording)
		
	elif args == 'disable':
		p.message(info('Disabling persistant demo recording'))
		persistent_recording = False
		sbserver.setRecordNextMatch(persistent_recording)
	else:
		raise UsageError()

