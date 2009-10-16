import sbserver
from xsbs.colors import red, orange, white
from xsbs.events import registerPolicyEventHandler, registerServerEventHandler
from UserPrivelege.userpriv import registerCommandHandler, masterRequired

muted_players = []

def allowMsg(cn, text):
	if cn in muted_players:
		sbserver.playerMessage(cn, red('You are currently muted.  No one will recieve your messages.'))
		return False
	return True

@masterRequired
def onMuteCommand(cn, args):
	try:
		args = args.split(' ')
		tcn = int(args[0])
		if len(args) > 1:
			raise KeyError
		if tcn not in muted_players:
			name = sbserver.playerName(tcn)
			muted_players.append(tcn)
			sbserver.message(orange(name) + white(' has been muted'))
		else:
			sbserver.playerMessage(cn, red('Player is already muted.'))
	except KeyError:
		sbserver.playerMessage(red('Usage: #mute <cn>'))
	except ValueError:
		sbserver.playerMessage(cn, red('Invalid player cn'))

@masterRequired
def onUnmuteCommand(cn, args):
	try:
		args = args.split(' ')
		tcn = int(args[0])
		if len(args) > 1:
			raise KeyError
		if tcn not in muted_players:
			sbserver.playerMessage(cn, red('Player is not crrently muted'))
		name = sbserver.playerName(tcn)
		muted_players.remove(tcn)
		sbserver.message(orange(name) + white(' has been unmuted'))
	except KeyError:
		sbserver.playerMessage(cn, red('Usage: #unmute <cn>'))
	except ValueError:
		sbserver.playerMessage(cn, red('Invalid player cn'))

def onDisconnect(cn):
	try:
		muted_players.remove(cn)
	except ValueError:
		pass

registerPolicyEventHandler('allow_message', allowMsg)
registerCommandHandler('mute', onMuteCommand)
registerCommandHandler('unmute', onUnmuteCommand)
registerServerEventHandler('player_disconnect', onDisconnect)

