from xsbs.events import eventHandler
from xsbs.settings import loadPluginConfig
from xsbs.ui import error, notice, warning, info
from xsbs.colors import colordict, green, orange
from xsbs.players import player, all as allPlayers, playerByName, playerByIpString
import sbserver
import time
import string


config = {
	'Main':
		{
			'spree_messages': 'yes',
			'multikill_messages': 'yes',
			'domination_messages': 'yes',
			
			'max_time_btwn_kills': 2
		},
	'SpreeMessages':
		{
			5:  '${green}${name} is on a ${orange}KILLING SPREE!',
			10: '${green}${name} is ${orange}UNSTOPPABLE!',
			15: '${green}${name} is ${orange}GODLIKE!',
			'killed': '${orange}${victimname}s killing spree ended by ${green}${killername}',
			'suicide': '${orange}${victimname} has ended their own killing spree'
		},
	'NeoMessages':
		{
			2:  '${orange}DOUBLE KILL!',
			3:  '${orange}TRIPLE KILL!',
			4:  '${orange}Quadrupal Kill!',
			5:  '${orange}OVERKILL!',
			7:  '${orange}KILLTACULAR!',
			10: '${orange}KILLOTROCITY!',
			15: '${orange}KILLTASTROPHE!',
			20: '${orange}KILLAPOCALYPSE!',
			25: '${orange}KILLIONAIRE!'
		},
	'DomMessages':
		{
			10: '${green}${killername} is ${orange}DOMINATING ${green}${victimname}',
			25: '${green}${killername} is ${orange}BRUTILIZING ${green}${victimname}'
		}
	}

def init():
	loadPluginConfig(config, 'OwnageMessages')
	
	config['Main']['spree_messages'] = config['Main']['spree_messages'] == 'yes'
	config['Main']['multikill_messages'] = config['Main']['multikill_messages'] == 'yes'
	config['Main']['domination_messages'] = config['Main']['domination_messages'] == 'yes'
	
	for index in config['SpreeMessages'].keys():
		config['SpreeMessages'][index] = string.Template(config['SpreeMessages'][index])
	for index in config['NeoMessages'].keys():
		config['NeoMessages'][index] = string.Template(config['NeoMessages'][index])
	for index in config['DomMessages'].keys():
		config['DomMessages'][index] = string.Template(config['DomMessages'][index])		


interval = config['Main']['max_time_btwn_kills']

class ownageData:
	def __init__(self, cn):
		self.playercn = cn
		self.last_kill_time = 0
		self.last_victim = -1
		self.current_victim = -2
		self.kills_since_death = 0
		self.ownage_count = 0
		self.last_ownage_count = 0
		self.domination_count = 0

		self.multikill_counts = {}
		for key in config['NeoMessages'].keys():
			self.multikill_counts[key] = 0
		
	#######public#######	
		
	def commit_kill(self, victimcn):
		self.kills_since_death += 1
		self.current_victim = victimcn
		self.current_kill_time = time.time()
		
		if config['Main']['spree_messages']:
			self.check_sprees()
		if config['Main']['multikill_messages']:
			self.check_ownage()
		if config['Main']['domination_messages']:
			self.check_domination()

		self.last_kill_time = self.current_kill_time	
		self.last_victim = self.current_victim

	
	def commit_death(self, killercn=-1):
		if killercn != -1:
			self.check_if_ending_spree(killercn)
	
		self.kills_since_death = 0
		self.last_kill_time = 0
		self.current_kill_time	= 10
		self.last_victim = -1
		self.current_victim = -2
		self.kills_since_death = 0
		self.ownage_count = 0
		self.last_ownage_count = 0
		self.domination_count = 0
		

	######private#######
	#implement traditional killing spree messages
	def check_sprees(self):
		if self.kills_since_death in config['SpreeMessages'].keys():
			sbserver.message(info(config['SpreeMessages'][self.kills_since_death].substitute(colordict, name=player(self.playercn).name())))
			
	def check_if_ending_spree(self, killercn):
		if self.kills_since_death >= 5:
			if killercn == -2:
				sbserver.message(info(config['SpreeMessages']['suicide'].substitute(colordict, victimname=player(self.playercn).name())))
			else:
				sbserver.message(info(config['SpreeMessages']['killed'].substitute(colordict, victimname=player(self.playercn).name(), killername=player(killercn).name())))
			

	#implement halo-like multi-kill messages
	def check_ownage(self):
		if (self.current_kill_time - self.last_kill_time) < interval:
			self.ownage_count += 1
			
			#check whether this level of multikill warrants a message
			if self.ownage_count in config['NeoMessages'].keys():
				try:
					player(self.playercn).message(info(config['NeoMessages'][self.ownage_count].substitute(colordict)))
				except ValueError:
					pass
				self.last_ownage_count = self.ownage_count
		else:
			#that multikill session ended so the multikill counter should be incremented
			if self.last_ownage_count != 0:
				self.multikill_counts[self.last_ownage_count] += 1
			self.ownage_count = 1
			

	#implement domination messsages
	def check_domination(self):
		if self.last_victim == self.current_victim:
			self.domination_count += 1
		else:
			self.domination_count = 0
		if self.domination_count in config['DomMessages'].keys():
			sbserver.message(info(config['DomMessages'][self.domination_count].substitute(colordict, killername=player(self.playercn).name(), victimname=player(self.last_victim).name())))

class ownageManager:
	def __init__(self):
		players = allPlayers()
		for p in players:
			p.ownagedata = ownageData(p.cn)
		
	def connect(self, cn):
		player(cn).ownagedata = ownageData(cn)
		
	def add_kill(self, killercn, victimcn):
		#updates the ownage datatype for the killer and victim
		killerplayer = player(killercn)
		victimplayer = player(victimcn)

		killerplayer.ownagedata.commit_kill(victimcn)
		victimplayer.ownagedata.commit_death(killercn)

		
	def suicide(self, cn):
			player(cn).ownagedata.commit_death(-2)
			
	def teamkill(self, killercn, victimcn):
		player(victimcn).ownagedata.commit_death(killercn)
		player(killercn).ownagedata.commit_death()
	

		
ownagemanager = ownageManager()

	
@eventHandler('map_changed')
def onMapCh(mapname, mapmode):
	ownagemanager = ownageManager()
	
@eventHandler('player_frag')
def onFrag(killercn, victimcn):
	ownagemanager.add_kill(killercn, victimcn)
	
@eventHandler('player_teamkill')
def onTK(killercn, victimcn):
	ownagemanager.teamkill(killercn, victimcn)
	
@eventHandler('player_connect')
def onDisconnect(cn):
	ownagemanager.connect(cn)
	
@eventHandler('game_bot_added')
def onDisconnect(cn):
	ownagemanager.connect(cn)
	
@eventHandler('player_suicide')
def onSuicide(cn):
	ownagemanager.suicide(cn)
	
init()
	
