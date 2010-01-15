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

class KillLog:
	def __init__(self):
		self.log = {}
	
	def add_kill(self, killercn, victimcn):
		if killercn in self.log.keys():
		
			killssincedeath = self.log[killercn][4] + 1
			self.log[killercn][5][0] = False
		
		
			if (time.time() - self.log[killercn][0]) < interval:
				wasownage = self.log[killercn][2] + 1
				self.log[killercn][5][1] = False
			else:
				wasownage = 1
				
			if victimcn == self.log[killercn][1]:
				wasdomination = self.log[killercn][3] + 1
				self.log[killercn][5][2] = False
			else:
				wasdomination = 1
			

		else:
			wasownage = 1
			wasdomination = 1
			killssincedeath = 1
				
		self.log[killercn] = (time.time(), victimcn, wasownage, wasdomination, killssincedeath, [False, False, False])
		
		if victimcn in self.log.keys():
			if self.log[victimcn][4] >= 5:
				sbserver.message(info(endmsg.substitute(victimname=sbserver.playerName(victimcn), killername=sbserver.playerName(killercn))))
			
		self.clearstats(victimcn)

	def set_said(self, cn, msg):
		if msg == 1:
			self.log[cn][5][0] = True
		elif msg == 2:
			self.log[cn][5][1] = True
		elif msg == 3:
			self.log[cn][5][2] = True
		
	def clearstats(self, cn):
		self.log[cn] = [0, -1, 0, 0, 0, [False, False, False]]
	
	def get_log(self):
		return self.log

killlog = KillLog()

def CheckForOwnage():
	log = killlog.get_log()
	
	for killercn in log.keys():
		#impliment traditional killing spree messages
		if spreemessagesenable:
			if log[killercn][4] > 1 and (not log[killercn][5][0]):
				for numkills in spreemessages.keys():
					if log[killercn][4] == numkills:
						sbserver.message(info(spreemessages[numkills].substitute(name=sbserver.playerName(killercn))))
						log[killercn][5][0] = True
		#impliment halo-like multi-kill messages
		if neomessagesenable:
			if log[killercn][2] > 1 and (not log[killercn][5][1]):
				for numkills in neomessages.keys():
					if log[killercn][2] == numkills:
						try:
							playerinst = player(killercn)
							playerinst.message(info(neomessages[numkills].substitute()))
							log[killercn][5][1] = True
						except (KeyError, ValueError):
							pass
		#impliment domination messsages.
		if dommessagesenable:
			if log[killercn][3] > 1 and (not log[killercn][5][2]):
				for numkills in dommessages.keys():
					if log[killercn][3] == numkills:
						sbserver.message(info(dommessages[numkills].substitute(killername=sbserver.playerName(killercn), victimname=sbserver.playerName(log[killercn][1]))))
						log[killercn][5][2] = True
	
	
	
@eventHandler('player_frag')
def onFrag(killercn, victimcn):
	killlog.add_kill(killercn, victimcn)
	CheckForOwnage()
	
@eventHandler('player_teamkill')
def onTK(killercn, victimcn):
	killlog.clearstats(killercn)
	
@eventHandler('player_disconnect')
def onDisconnect(cn):
	killlog.clearstats(cn)
	
@eventHandler('player_suicide')
def onSuicide(cn):
	killlog.clearstats(cn)
	