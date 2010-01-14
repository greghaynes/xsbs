from xsbs.commands import commandHandler, UsageError
from xsbs.events import eventHandler
from xsbs.settings import PluginConfig
from xsbs.ui import error, notice, warning
from Bans.bans import ban
from xsbs.colors import colordict, green
from xsbs.players import player, all as allPlayers, playerByName, playerByIpString
from UserPrivilege.userpriv import masterRequired
import sbserver
import time
import string

config = PluginConfig('nospam')
interval = int(config.getOption('Config', 'action_interval', '5'))
max_per_interval = int(config.getOption('Config', 'max_msgs', '6'))
instakickmsgs = int(config.getOption('Config', 'instakickmsgs', '3'))
ban_duration = int(config.getOption('Config', 'ban_time', '3600'))
warnings = int(config.getOption('Config', 'warnings', '3'))
warn_spam_message = config.getOption('Config', 'warn_spam_message', 'Warning do not spam. This server is ${red}spam intollerant!${white} ')
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
		playerByIpString(ip).message(warning(warn_spam_message.substitute(colordict)))
	
		if ip in self.spammerlist.keys():
			self.spammerlist[ip] += 1
			if self.spammerlist[ip] > warnings:
				self.dealwithspammer(ip)
				del self.spammerlist[ip]
		else:
			self.spammerlist[ip] = 1

	def dealwithspammer(self, ip):
		playercn = playerByIpString(ip).cn
		ban(playercn, ban_duration, 'spamming server', -1)
		

chatlog = ChatLog()
spammermanager = SpammerManager()


@eventHandler('player_message')
def onMessage(cn, text):
	chatlog.add_chat(cn, text)
	chatlog.clean_chat()
	log = chatlog.get_log()
	
	cn_1secoccurance = {}
	for timekey in log.keys():
		if (time.time() - timekey) <= 1:
			chatcn = log[timekey][0]
			if not chatcn in cn_1secoccurance.keys():
				cn_1secoccurance[chatcn] = 1
			else:
				cn_1secoccurance[chatcn] += 1

	
	for occur in cn_1secoccurance.keys():
		if cn_1secoccurance[occur] > instakickmsgs:
			spammermanager.add_spamming_case(player(occur).ipString())
				
	cn_occurance = {}
	for timekey in log.keys():
		chatcn = log[timekey][0]
		if not chatcn in cn_occurance.keys():
			cn_occurance[chatcn] = 1
		else:
			cn_occurance[chatcn] += 1
	
	
	for occur in cn_occurance.keys():
		if cn_occurance[occur] > max_per_interval:
			spammermanager.add_spamming_case(player(occur).ipString())
	