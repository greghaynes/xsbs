import sbevents, sbserver
from Bans.bans import ban

class PingLimiter:
	def __init__(self):
		self.max_ping = 600 
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
				sbserver.playerMessage(cn, 'Your ping is too high.  You will be kicked if it is not lowered.')
				self.warned_cns.append(lagger)
				i += 1
		sbevents.timerman.addTimer(5000, limiter.checkPlayers, ())

limiter = PingLimiter()
sbevents.timerman.addTimer(5000, limiter.checkPlayers, ())

