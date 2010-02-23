from xsbs.events import eventHandler
from xsbs.settings import PluginConfig
from xsbs.ui import error, notice, warning, info
from xsbs.colors import colordict, green, orange
from xsbs.players import player, all as allPlayers, playerByName, playerByIpString
import sbserver
import time
import string

config = PluginConfig('ownage')
spreemessagesenable = config.getOption('Config', 'spreemessages', 'yes') == 'yes'
neomessagesenable = config.getOption('Config', 'neomessages', 'yes') == 'yes'
dommessagesenable = config.getOption('Config', 'dommessages', 'yes') == 'yes'
interval = int(config.getOption('Config', 'max_time_btwn_kills', '2'))
del config

spreemessages = { 
	5: string.Template(green('$name') + ' is on a ' + orange('KILLING SPREE!')),
	10: string.Template(green('$name') + ' is ' + orange('UNSTOPPABLE!')),
	15: string.Template(green('$name') + ' is ' + orange('GODLIKE!')) 
	}
endmsg = string.Template(orange('$victimname') + '\'s killing spree ended by ' + green('$killername'))
suicideendmsg = string.Template(orange('$victimname') + ' has ended his own killing spree!')

neomessages = { 
	2: string.Template(orange('DOUBLE KILL!')),
	3: string.Template(orange('TRIPLE KILL!')),
	5: string.Template(orange('OVERKILL!')),
	7: string.Template(orange('KILLTACULAR!')),
	10: string.Template(orange('KILLOTROCITY!')),
	15: string.Template(orange('KILLTASTROPHE!')),
	20: string.Template(orange('KILLAPOCALYPSE!')),
	25: string.Template(orange('KILLIONAIRE!'))
	}
	
dommessages = {
	10: string.Template(green('$killername') + ' is ' + orange('DOMINATING ') + green('$victimname')),
	25: string.Template(green('$killername') + ' is ' + orange('BRUTILIZING ') + green('$victimname'))
	}

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
		for key in neomessages.keys():
			self.multikill_counts[key] = 0
		
	#######public#######	
		
	def commit_kill(self, victimcn):
		self.kills_since_death += 1
		self.current_victim = victimcn
		self.current_kill_time = time.time()
		
		if spreemessagesenable:
			self.check_sprees()
		if neomessagesenable:
			self.check_ownage()
		if dommessagesenable:
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
		if self.kills_since_death in spreemessages.keys():
			sbserver.message(info(spreemessages[self.kills_since_death].substitute(name=player(self.playercn).name())))
			
	def check_if_ending_spree(self, killercn):
		if self.kills_since_death >= 5:
			if killercn == -2:
				sbserver.message(info(suicideendmsg.substitute(victimname=player(self.playercn).name())))
			else:
				sbserver.message(info(endmsg.substitute(victimname=player(self.playercn).name(), killername=player(killercn).name())))
			

	#implement halo-like multi-kill messages
	def check_ownage(self):
		if (self.current_kill_time - self.last_kill_time) < interval:
			self.ownage_count += 1
			
			#check whether this level of multikill warrants a message
			if self.ownage_count in neomessages.keys():
				try:
					player(self.playercn).message(info(neomessages[self.ownage_count].substitute()))
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
		if self.domination_count in dommessages.keys():
			sbserver.message(info(dommessages[self.domination_count].substitute(killername=player(self.playercn).name(), victimname=player(self.last_victim).name())))

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
	