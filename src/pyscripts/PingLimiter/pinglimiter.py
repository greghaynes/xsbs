import sbserver
from xsbs.timers import addTimer
from Bans.bans import ban
from xsbs.settings import PluginConfig
from xsbs.ui import warning

config = PluginConfig('pinglimiter')
max_ping = config.getOption('Config', 'max_ping', '600')
del config
max_ping = int(max_ping)

class PingLimiter:
	def __init__(self, max_ping):
		self.max_ping = max_ping
		self.warned_cns = []
	def checkPlayers(self):
		laggers = []
		for cn in sbserver.players():
			if sbserver.playerPing(cn) > self.max_ping:
				laggers.append(cn)
		i = 0
		for lagger in laggers:
			if lagger in self.warned_cns:
				ban(cn, 0, 'lagging')
				del laggers[i]
			else:
				sbserver.playerMessage(cn, warning('Your ping is too high.  You will be kicked if it is not lowered.'))
				self.warned_cns.append(lagger)
				i += 1
		addTimer(5000, limiter.checkPlayers, ())

limiter = PingLimiter(max_ping)
addTimer(5000, limiter.checkPlayers, ())

