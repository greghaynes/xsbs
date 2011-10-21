from xsbs.events import eventHandler
from xsbs.timers import addTimer
from xsbs.settings import PluginConfig
from xsbs.ui import error, notice, warning
from Bans.bans import ban
from xsbs.colors import colordict
from xsbs.players import player, all as allPlayers, playerByName, playerByIpString
import sbserver
import time
import string

config = PluginConfig('nospam')
interval = 			int(config.getOption('Config', 'action_interval', '5'))
max_per_interval = 	int(config.getOption('Config', 'max_msgs', '6'))
max_per_second = 	int(config.getOption('Config', 'max_msgs_per_sec', '3'))
ban_duration = 		int(config.getOption('Config', 'ban_time', '3600'))
warnings = 			int(config.getOption('Config', 'warnings', '2'))
warn_spam_message = config.getOption('Config', 'warn_spam_message', 'Warning do not spam. This server is ${red}spam intolerant!${white} ')
del config
warn_spam_message = string.Template(warn_spam_message)

class ChatLog:
	def __init__(self):
		self.log = {}

	def add_chat(self, cn, text):
		speakin = player(cn)
		ip = speakin.ipString()
		self.log[time.time()] = (cn, ip, text)

	def clean_chat(self):
		for timekey in self.log.keys():
			if (time.time() - timekey) > interval:
				del self.log[timekey]

	def get_log(self):
		return self.log

class SpammerManager:
	def __init__(self):
		self.spammerlist = {}

	def add_spamming_case(self, ip):
		if ip in self.spammerlist.keys():
			self.spammerlist[ip] += 1
			if self.spammerlist[ip] > warnings:
				self.dealwithspammer(ip)
				del self.spammerlist[ip]
			else:
				playerByIpString(ip).message(warning(warn_spam_message.substitute(colordict)))
		else:
			self.spammerlist[ip] = 1
			playerByIpString(ip).message(warning(warn_spam_message.substitute(colordict)))

	def dealwithspammer(self, ip):
		try:
			playercn = playerByIpString(ip).cn
			ban(playercn, ban_duration, 'spamming server', -1)
		except ValueError:
			print "Error while banning spamming player by IP"

chatlog = ChatLog()
spammermanager = SpammerManager()


@eventHandler('player_message')
def onMessage(cn, text):
	chatlog.add_chat(cn, text)
	chatlog.clean_chat()


def CheckForSpammers():
	#sbserver.message("Check for spammers ran")
	log = chatlog.get_log()

	cn_occurs_1sec = {}
	cn_occurs_interval = {}
	for timekey in log.keys():
		chatcn = log[timekey][0]
		if (time.time() - timekey) <= 1:
			if not chatcn in cn_occurs_1sec.keys():
				cn_occurs_1sec[chatcn] = 1
			else:
				cn_occurs_1sec[chatcn] += 1

		if not chatcn in cn_occurs_interval.keys():
			cn_occurs_interval[chatcn] = 1
		else:
			cn_occurs_interval[chatcn] += 1


	for occur in cn_occurs_1sec.keys():
		if cn_occurs_1sec[occur] > max_per_second:
			spammermanager.add_spamming_case(player(occur).ipString())
		else:
			for occur in cn_occurs_interval.keys():
				if cn_occurs_interval[occur] > max_per_interval:
					spammermanager.add_spamming_case(player(occur).ipString())

def checkforspammerstimer():
	CheckForSpammers()
	addTimer(1000, checkforspammerstimer, ())

addTimer(1000, checkforspammerstimer, ())
