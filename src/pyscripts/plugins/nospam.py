from xsbs.events import eventHandler
from xsbs.timers import addTimer
from xsbs.settings import loadPluginConfig
from xsbs.ui import error, notice, warning, themedict
from xsbs.ban import ban
from xsbs.players import player, all as allPlayers, playerByName, playerByIpString
import sbserver
import time
import string

import copy

config = {
	'Main':
		{
			'enabled': 'yes',
			'action_interval': 5,
			'max_msgs': 6,
			'max_msgs_per_sec': 3,
			'ban_time': 3600,
			'warnings': 2,
		},
	'Templates':
		{
			'message': 'Warning do not spam. This server is ${severe_action}spam intolerant!${text} ',
		}
	}

def init():
	loadPluginConfig(config, 'NoSpam')
	config['Templates']['message'] = string.Template(config['Templates']['message'])
	config['Main']['action_interval'] = int(config['Main']['action_interval'])
	config['Main']['max_msgs'] = int(config['Main']['max_msgs'])
	config['Main']['max_msgs_per_sec'] = int(config['Main']['max_msgs_per_sec'])
	config['Main']['ban_time'] = int(config['Main']['ban_time'])
	config['Main']['warnings'] = int(config['Main']['warnings'])
	

class ChatLog:
	def __init__(self):
		self.log = {}
	
	def add_chat(self, cn, text):
		speakin = player(cn)
		ip = speakin.ipString()
		self.log[time.time()] = (cn, ip, text)
		
	def clean_chat(self):
		for timekey in self.log.keys():
			if (time.time() - timekey) > config['Main']['action_interval']:
				del self.log[timekey]
			
	def get_log(self):
		return self.log
		
class SpammerManager:
	def __init__(self):
		self.spammerlist = {}
		
	def add_spamming_case(self, ip):
		if ip in self.spammerlist.keys():
			self.spammerlist[ip] += 1
			if self.spammerlist[ip] > config['Main']['warnings']:
				self.dealwithspammer(ip)
				del self.spammerlist[ip]
			else:
				playerByIpString(ip).message(warning(config['Templates']['message'].substitute(themedict)))
		else:
			self.spammerlist[ip] = 1
			playerByIpString(ip).message(warning(config['Templates']['message'].substitute(themedict)))

	def dealwithspammer(self, ip):
		try:
			playercn = playerByIpString(ip).cn
			ban(playercn, config['Main']['ban_time'], 'spamming server', -1)
		except ValueError:
			print "Error while banning spamming player by IP"
			
chatlog = ChatLog()
spammermanager = SpammerManager()
			
	
def CheckForSpammers():
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
		if cn_occurs_1sec[occur] > config['Main']['max_msgs_per_sec']:
			spammermanager.add_spamming_case(player(occur).ipString())
		else:
			for occur in cn_occurs_interval.keys():
				if cn_occurs_interval[occur] > config['Main']['max_msgs']:
					spammermanager.add_spamming_case(player(occur).ipString())


def checkforspammerstimer():
	CheckForSpammers()
	addTimer(1000, checkforspammerstimer, ())

init()

addTimer(1000, checkforspammerstimer, ())

@eventHandler('player_message')
def onMessage(cn, text):
	chatlog.add_chat(cn, text)
	chatlog.clean_chat()
