import sbserver
from xsbs.commands import commandHandler, UsageError
from xsbs.events import eventHandler
from xsbs.ui import info, notice
from xsbs.settings import loadPluginConfig
from xsbs.players import player, masterRequired, adminRequired
from xsbs.ui import insufficientPermissions, themedict
import string
import logging

config = {
	'Main': {
		'persistent_recording': 'no',
		'required_permissions': 1
		},
	'Templates': {
		'record_next_message': 'Demo recording is ${action} for next match (by ${client_name}${user}${text})'
		}
	}
	
loadPluginConfig(config, 'Demos')

persistent_recording = config['Main']['persistent_recording'] == 'yes'
required_permissions = config['Main']['required_permissions']

action_temp = string.Template(config['Templates']['record_next_message'])

def permissions_ok(p):
	if required_permissions == 0:
		return True
	if required_permissions == 1:
		return p.isMaster()
	if required_permissions == 2:
		return p.isAdmin()
	logging.error('required_permissions not a valid int!')
	return False
	
	
@eventHandler('player_record_demo')
def playerRecordNextMatch(p, val):
	if permissions_ok(p):
		if val == sbserver.nextMatchRecorded():
			return
		if val:
			act = 'enabled'
		else:
			act = 'disabled'
		sbserver.setRecordNextMatch(val)
		sbserver.message(notice(action_temp.substitute(themedict, action=act, user=p.name())))
	else:
		insufficientPermissions(p.cn)


@eventHandler('map_changed')
def persistRecordNextMatch(themap, themode):
	global persistent_recording
	if persistent_recording:
		sbserver.setRecordNextMatch(True)


@commandHandler('persistdemo')
@adminRequired
def setPersistantDemoRecord(p, args):
	'''@description Enable/disable persistant demo recording
	   @usage enable/disable'''
	global persistent_recording
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
		
