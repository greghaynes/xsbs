import sbserver
from ConfigParser import NoOptionError
from xsbs.settings import PluginConfig
from xsbs.events import registerServerEventHandler
import asyncore, socket

config = PluginConfig('ircbot')
channel = config.getOption('Config', 'channel', '#xsbs-newserver')
servername = config.getOption('Config', 'servername', 'irc.gamesurge.net')
nickname = config.getOption('Config', 'nickname', 'xsbs-newbot')
port = int(config.getOption('Config', 'port', '6667'))
try:
	ipaddress = config.getOption('Config', 'ipaddress', None, False)
except NoOptionError:
	ipaddress = None

class IrcBot(asyncore.dispatcher):
	def __init__(self, servername, nickname, port=6667):
		asyncore.dispatcher.__init__(self)
		self.servername = servername
		self.nickname = nickname
		self.port = port
		self.isConnected = False
		self.channels = []
		self.buff = ''
		self.msgcommands = {
				'status': self.sendStatus
		}
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		if ipaddress != None:
			self.bind((ipaddress, 0))
		self.connect((self.servername, self.port))
		self.connect_count = 1
		self.sendNick()
	def __del__(self):
		self.close()
	def quit(self):
		self.send('QUIT :XSBS - eXtensible SauerBraten Server\r\n')
	def handle_close(self):
		print 'IRC Bot: connection closed.'
		print 'IRC Bot: reconnecting...'
		self.connect_count += 1
		if self.connect_count >= 5:
			print 'IRC Bot: Connect failed 5 times.  Quitting.'
		else:
			self.connect((self.servername, self.port))
	def handle_connect(self):
		print 'IRC Bot: conneced'
		self.connect_count = 0
	def handle_write(self):
		sent = self.send(self.writebuff)
		self.writebuff = self.writebuff[sent:]
	def writeable(self):
		return len(self.writebuff) > 0
	def sendNick(self):
		self.writebuff = 'NICK %s\r\n' % self.nickname
		self.writebuff += 'USER %s %s %s :%s\r\n' % (self.nickname, self.nickname, self.nickname, self.nickname)
	def onWelcome(self):
		self.isConnected = True
		for channel in self.channels:
			self.join(channel)
		del self.channels[:]
	def join(self, channel):
		if self.isConnected:
			self.writebuff += 'JOIN %s\r\n' % channel
		else:
			self.channels.append(channel)
	def privMsg(self, user, message):
		self.writebuff += 'PRIVMSG %s :%s\r\n' % (user, message)
	def sendStatus(self, sender, message):
		clients = sbserver.clients()
		players = sbserver.players()
		msg = '%i clients: %i players, %i spectators' % (len(clients), len(players), len(clients) - len(players))
		self.privMsg(channel, msg)
	def handle_privmsg(self, sender, message):
		if message[0] == '!':
			try:
				self.msgcommands[message[1:]](sender, message)
			except KeyError:
				self.privMsg(channel, 'Invalid command')
		else:
			sbserver.message('(Remote User) %s: %s' % (sender, message))
	def handle_read(self):
		self.buff += self.recv(4096)
		tmp_buff = self.buff.split('\n')
		self.buff = tmp_buff.pop()
		for line in tmp_buff:
			line = line.strip().split()
			if line[0] == 'PING':
				self.writebuff += 'PONG %s\r\n' % line[1]
			elif line[1] == 'MODE':
				if not self.isConnected and line[3] == ':+iw':
					self.onWelcome()
			elif line[1] == 'PRIVMSG':
				user = line[0].split('!')[0][1:]
				text = line[3][1:]
				if len(line) >= 4:
					for t in line[4:]:
						text += ' '
						text += t
				self.handle_privmsg(user, text)
			elif line[1] == '433':
				print 'IRC Bot: Nickname is in use!'
				self.nickname = self.nickname + '1'
				print 'IRC Bot: Using %s' % self.nickname
				self.sendNick()

bot = IrcBot(servername, nickname, port)
bot.join(channel)

def onPlayerActive(cn):
	bot.privMsg(channel, 'CONNECT         Player %s (%i) has joined' % (sbserver.playerName(cn), cn))

def onPlayerDisconnect(cn):
	bot.privMsg(channel, 'DISCONNECT      Player %s (%i) has disconnected' % (sbserver.playerName(cn), cn))

def onMsg(cn, text):
	bot.privMsg(channel, 'MESSAGE         %s (%i): %s' % (sbserver.playerName(cn), cn, text))

def onTeamMsg(cn, text):
	bot.privMsg(channel, 'MESSAGE (TEAM)  %s (%i) (Team): %s' % (sbserver.playerName(cn), cn, text))

def onMapChange(map, mode):
	bot.privMsg(channel, 'MAP CHANGE      %s (%s)' % (map, sbserver.modeName(mode)))

def onReload():
	bot.quit()

def onStop():
	bot.quit()

event_abilities = {
	'player_active': ('player_active', onPlayerActive),
	'player_disconnect': ('player_disconnect', onPlayerDisconnect),
	'message': ('player_message', onMsg),
	'message_team': ('player_message_team', onTeamMsg),
	'map_change': ('map_changed', onMapChange),
}

for key in event_abilities.keys():
	if config.getOption('Abilities', key, 'no') == 'yes':
		ev = event_abilities[key]
		registerServerEventHandler(ev[0], ev[1])
del config

registerServerEventHandler('reload', onReload)
registerServerEventHandler('server_stop', onStop)

