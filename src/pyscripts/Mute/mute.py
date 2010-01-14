import sbserver
from xsbs.colors import colordict
from xsbs.ui import info, notice, error
from xsbs.events import registerPolicyEventHandler, registerServerEventHandler
from xsbs.players import player, masterRequired
from xsbs.settings import PluginConfig
from xsbs.commands import commandHandler, UsageError, StateError
import string

config = PluginConfig('mute')
muted_temp = config.getOption('Messages', 'muted_message', '${green}${muted_name}${white} has been ${red}muted ${white}(by ${blue}${muter}${white})')
unmuted_temp = config.getOption('Messages', 'unmuted_message', '${green}${muted_name}${white} has been ${red}unmuted ${white}(by ${blue}${muter}${white})')
del config
muted_temp = string.Template(muted_temp)
unmuted_temp = string.Template(unmuted_temp)
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
def onMuteSpectatorsCmd(cn, args):
	'''@description Mute all spectators
	   @usage'''
	if args == '':
		if mute_spectators[0] == True:
			raise StateError('Spectators are arleady muted')
		else:
			mute_spectators[0] = True
			sbserver.message(notice('Spectators are now muted'))
	else:
		raise UsageError()

@commandHandler('unmutespectators')
@masterRequired
def onUnMuteSpectatorsCmd(cn, args):
	'''@description Unmute spectators
	   @usage'''
	if args == '':
		if mute_spectators[0] == False:
			raise StateError('Spectators are not currently muted')
		else:
			mute_spectators[0] = False
			sbserver.message(notice('Spectators are no longer muted'))
	else:
		raise UsageError()

@commandHandler('mute')
@masterRequired
def onMuteCommand(cn, args):
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
				muter = player(cn).name()
				sbserver.message(info(muted_temp.substitute(colordict, muted_name=name, muter=muter)))
	except KeyError:
		raise UsageError()
			
@commandHandler('unmute')
@masterRequired
def onUnmuteCommand(cn, args):
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
				muter = player(cn).name()
				sbserver.message(info(unmuted_temp.substitute(colordict, muted_name=p.name(), muter=muter)))
			else:
				sbserver.playerMessage(cn, error('Specified player is not crrently muted'))
		except AttributeError:
			sbserver.playerMessage(cn, error('Specified player is not currently muted.'))
	except KeyError:
		raise UsageError()
	except ValueError:
		sbserver.playerMessage(cn, error('Invalid player cn'))

registerPolicyEventHandler('allow_message', allowMsg)

