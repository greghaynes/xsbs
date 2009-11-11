import sbserver
from xsbs.colors import colordict
from xsbs.ui import info, notice, error
from xsbs.events import registerPolicyEventHandler, registerServerEventHandler
from xsbs.players import player
from xsbs.settings import PluginConfig
from UserPrivilege.userpriv import registerCommandHandler, masterRequired
import string

config = PluginConfig('mute')
muted_temp = config.getOption('Messages', 'muted_message', '${green}${muted_name}${white} has been ${red}muted')
unmuted_temp = config.getOption('Messages', 'unmuted_message', '${green}${muted_name}${white} has been ${red}unmuted')
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

@masterRequired
def onMuteSpectatorsCmd(cn, args):
	if args == '':
		if mute_spectators[0] == True:
			player(cn).message(error('Spectators are arleady muted'))
		else:
			mute_spectators[0] = True
			sbserver.message(notice('Spectators are now muted'))
	else:
		player(cn).message(error('Usage: #mutespectators'))

@masterRequired
def onUnMuteSpectatorsCmd(cn, args):
	if args == '':
		if mute_spectators[0] == False:
			player(cn).message(error('Spectators are not currently muted'))
		else:
			mute_spectators[0] = False
			sbserver.message(notice('Spectators are no longer muted'))
	else:
		player(cn).message(error('Usage: #unmutespectators'))

@masterRequired
def onMuteCommand(cn, args):
	try:
		args = args.split(' ')
		tcn = int(args[0])
		if len(args) > 1:
			raise KeyError
		try:	
			p = player(tcn)
		except ValueError:
			sbserver.playerMessage(cn, errer('Invalid player cn'))
		else:
			try:
				muted = p.is_muted
			except AttributeError:
			 	muted = False
			if muted:
				sbserver.playerMessage(cn, error('Player is already muted.'))
			else:
				p.is_muted = True
				name = sbserver.playerName(tcn)
				sbserver.message(info(muted_temp.substitute(colordict, muted_name=name)))
	except KeyError:
		sbserver.playerMessage(cn, error('Usage: #mute <cn>'))
			
@masterRequired
def onUnmuteCommand(cn, args):
	try:
		args = args.split(' ')
		tcn = int(args[0])
		if len(args) > 1:
			raise KeyError
		try:
			if player(tcn).is_muted:
				player(tcn).is_muted = False
				sbserver.message(info(unmuted_temp.substitute(colordict, muted_name=sbserver.playerName(tcn))))
			else:
				sbserver.playerMessage(cn, error('Specifiedlayer is not crrently muted'))
		except AttributeError:
			sbserver.playerMessage(cn, error('Specified player is not currently muted.'))
	except KeyError:
		sbserver.playerMessage(cn, error('Usage: #unmute <cn>'))
	except ValueError:
		sbserver.playerMessage(cn, error('Invalid player cn'))

registerPolicyEventHandler('allow_message', allowMsg)
registerCommandHandler('mutespectators', onMuteSpectatorsCmd)
registerCommandHandler('unmutespectators', onUnMuteSpectatorsCmd)
registerCommandHandler('mute', onMuteCommand)
registerCommandHandler('unmute', onUnmuteCommand)

