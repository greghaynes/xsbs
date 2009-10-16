import sbserver
from xsbs.colors import colordict
from xsbs.ui import info, notice, error
from xsbs.events import registerPolicyEventHandler, registerServerEventHandler
from xsbs.players import player
from xsbs.settings import PluginConfig
from UserPrivelege.userpriv import registerCommandHandler, masterRequired
import string

config = PluginConfig('mute')
muted_temp = config.getOption('Messages', 'muted_message', '${green}${muted_name}${white} has been ${red}muted')
unmuted_temp = config.getOption('Messages', 'unmuted_message', '${green}${muted_name}${white} has been ${red}unmuted')
del config
muted_temp = string.Template(muted_temp)
unmuted_temp = string.Template(unmuted_temp)

def allowMsg(cn, text):
	try:
		if player(cn).is_muted:
			sbserver.playerMessage(cn, notice('You are currently muted.  No one will recieve your messages.'))
			return False
	except AttributeError:
		pass
	return True

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
		if player(tcn).is_muted:
			player(tcn).is_muted = False
			sbserver.message(info(unmuted_temp.substitute(colordict, muted_name=sbserver.playerName(tcn))))
		else:
			sbserver.playerMessage(cn, error('Player is not crrently muted'))
	except KeyError:
		sbserver.playerMessage(cn, error('Usage: #unmute <cn>'))
	except ValueError:
		sbserver.playerMessage(cn, error('Invalid player cn'))

def onDisconnect(cn):
	try:
		muted_players.remove(cn)
	except ValueError:
		pass

registerPolicyEventHandler('allow_message', allowMsg)
registerCommandHandler('mute', onMuteCommand)
registerCommandHandler('unmute', onUnmuteCommand)
registerServerEventHandler('player_disconnect', onDisconnect)

