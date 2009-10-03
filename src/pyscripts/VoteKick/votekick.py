from xsbs.events import registerServerEventHandler
from xsbs.commands import registerCommandHandler
from xsbs.players import player, all as allPlayers
from xsbs.ui import error, info
from Bans.bans import ban
import sbserver

def checkVotes(cn):
	players = allPlayers()
	needed = len(players) / 2
	if needed <= 1:
		needed += 1
	votes = 0
	for player in players:
		if player.votekick == cn:
			votes += 1
	if votes > needed:
		ban(cn, 3600, 'Vote', -1)

def onVoteKick(cn, args):
	if args == '':
		sbserver.playerMessage(cn, error('Usage #votekick <cn>'))
	else:
		try:
			tcn = int(args)
			if player(cn).votekick == tcn:
				sbserver.playerMessage(cn, error('You have already voted to kick that player.'))
				allow_vote = False
			else:
				allow_vote = True
		except AttributeError:
			allow_vote = True
		if allow_vote:
			sbserver.message(info('%s has voted to kick %s' % (sbserver.playerName(cn), sbserver.playerName(tcn))))
			player(cn).votekick = int(args)
			checkVotes(int(args))

registerCommandHandler('votekick', onVoteKick)

