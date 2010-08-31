import sbserver
from xsbs.ui import info, notice, error, themedict
from xsbs.events import registerPolicyEventHandler, registerServerEventHandler
from xsbs.players import player, masterRequired
from xsbs.settings import loadPluginConfig
from xsbs.commands import commandHandler, UsageError, StateError, ArgumentValueError
import string

config = {
	'Main':
		{
			'allow_mode_vote': 'no',
			'lock_game_mode': 'no',
		},
	'Templates':
		{
			'muted_message': '${client_name}${muted_name}${text} has been ${severe_action}muted ${text}(by ${secondary_client_name}${muter}${text})',
			'unmuted_message': '${client_name}${muted_name}${text} has been ${severe_action}unmuted ${text}(by ${secondary_client_name}${muter}${text})',
		}
	}

def init():
	loadPluginConfig(config, 'Mute')
	config['Templates']['muted_message'] = string.Template(config['Templates']['muted_message'])
	config['Templates']['unmuted_message'] = string.Template(config['Templates']['unmuted_message'])

mute_spectators = [False]

def allowMsg(cn, text):
	try:
		p = player(cn)
		if mute_spectators[0] == True and p.isSpectator():
			p.message(notice('Spectators are currently muted.  No one will recieve your message'))
			return False
		if p.is_muted:
			p.message(notice('You are currently muted.  No one will recieve your message'))
			return False
	except (AttributeError, ValueError):
		pass
	return True

@commandHandler('mutespectators')
@masterRequired
def onMuteSpectatorsCmd(p, args):
	'''@description Mute all spectators
	   @usage'''
	if args == '':
		if mute_spectators[0] == True:
			raise StateError('Spectators are arleady muted')
		else:
			mute_spectators[0] = True
			sbserver.message(notice('Spectators are now muted'))
	else:
		raise ExtraArgumentError()

@commandHandler('unmutespectators')
@masterRequired
def onUnMuteSpectatorsCmd(p, args):
	'''@description Unmute spectators
	   @usage'''
	if args == '':
		if mute_spectators[0] == False:
			raise StateError('Spectators are not currently muted')
		else:
			mute_spectators[0] = False
			sbserver.message(notice('Spectators are no longer muted'))
	else:
		raise ExtraArgumentError()

@commandHandler('mute')
@masterRequired
def onMuteCommand(sender, args):
	'''@description Mute a player
	   @usage cn'''
	try:
		args = args.split(' ')
		tcn = int(args[0])
		if len(args) > 1:
			raise KeyError
		try:	
			p = player(tcn)
		except ValueError:
			raise StateError('Invalid player cn')
		else:
			try:
				muted = p.is_muted
			except AttributeError:
			 	muted = False
			if muted:
				raise StateError('Player is already muted.')
			else:
				p.is_muted = True
				name = p.name()
				muter = player(sender.cn).name()
				sbserver.message(info(config['Templates']['muted_message'].substitute(themedict, muted_name=name, muter=muter)))
	except KeyError:
		raise UsageError()
			
@commandHandler('unmute')
@masterRequired
def onUnmuteCommand(sender, args):
	'''@description Unmute a player
	   @usage cn'''
	try:
		args = args.split(' ')
		tcn = int(args[0])
		if len(args) > 1:
			raise KeyError
		try:
			p = player(tcn)
			if p.is_muted:
				p.is_muted = False
				muter = player(sender.cn).name()
				sbserver.message(info(config['Templates']['unmuted_message'].substitute(themedict, muted_name=p.name(), muter=muter)))
			else:
				raise StateError('Specified player is not crrently muted')
		except AttributeError:
			raise StateError('Specified player is not currently muted.')
	except KeyError:
		raise UsageError('No cn specified')
	except ValueError:
		raise ArgumentValueError('Invalid player cn')

registerPolicyEventHandler('allow_message', allowMsg)

init()

