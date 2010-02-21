from xsbs.events import registerServerEventHandler
from xsbs.commands import commandHandler
from xsbs.players import player, all as allPlayers
from xsbs.ui import error, info
from xsbs.colors import colordict
from xsbs.settings import PluginConfig
from xsbs.ban import ban
import sbserver
import string

config = PluginConfig('votekick')
vktemp = config.getOption('Config', 'vote_message', '${green}${voter}${white} voted to ${red}kick ${orange}${victim}')
del config
vktemp = string.Template(vktemp)

def checkVotes(cn):
	players = allPlayers()
	needed = len(players) / 2
	if needed <= 1:
		needed += 1
	votes = 0
	for player in players:
		try:
			if player.votekick == cn:
				votes += 1
		except AttributeError:
			pass
	if votes >= needed:
		ban(cn, 3600, 'Vote', -1)

@commandHandler('votekick')
def onVoteKick(p, args):
	'''@description Vote to kick a player from server
	   @usage <cn>'''
	if args == '':
		p.message(error('Usage #votekick <cn>'))
	else:
		try:
			tcn = int(args)
			if p.votekick == tcn:
				p.message(error('You have already voted to kick that player.'))
				allow_vote = False
			else:
				allow_vote = True
		except AttributeError:
			allow_vote = True
		if allow_vote:
			sbserver.message(info(vktemp.substitute(colordict, voter=p.name(), victim=sbserver.playerName(tcn))))
			p.votekick = int(args)
			checkVotes(int(args))

