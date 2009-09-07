import sbevents, sbserver
import socket
from ConfigParser import ConfigParser

channel = ''
servername = ''
nickname = ''
port = 6667

class IrcBot:
	def __init__(self, servername, nickname, port=6667):
		self.servername = servername
		self.nickname = nickname
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setblocking(0)
		self.isConnected = False
		self.channels = []
		self.msg_handlers = []
	def connect(self):
		sbevents.sockmon.onRead(self.socket, self.onConnect, (), False)
		try:
			self.socket.connect((self.servername, self.port))
		except:
			pass
	def onConnect(self):
		sbevents.sockmon.onRead(self.socket, self.processData, (), True)
		self.buff = self.socket.recv(4096)
		self.socket.send('NICK %s\r\n' % self.nickname)
		self.socket.send('USER %s %s %s :%s\r\n' % (self.nickname, self.nickname, self.nickname, self.nickname))
	def onWelcome(self):
		self.isConnected = True
		for channel in self.channels:
			self.join(channel)
		del self.channels[:]
	def join(self, channel):
		if self.isConnected:
			self.socket.send('JOIN %s\r\n' % channel)
		else:
			self.channels.append(channel)
	def privMsg(self, user, message):
		self.socket.send('PRIVMSG %s :%s\r\n' % (user, message))
	def processData(self):
		self.buff += self.socket.recv(4096)
		tmp_buff = self.buff.split('\n')
		self.buff = tmp_buff.pop()
		for line in tmp_buff:
			line = line.strip().split()
			if line[0] == 'PING':
				self.socket.send('PONG %s\r\n' % line[1])
			elif line[1] == 'MODE':
				if not self.isConnected and line[3] == ':+iw':
					self.onWelcome()
			elif line[1] == 'PRIVMSG':
				user = line[0].split('!')[0]
				text = line[3][1:]
				for handler in self.msg_handlers:
					handler(self, user, text)

config = ConfigParser()
config.read('IrcBot/plugin.conf')

if config.has_option('Bot', 'servername'):
	servername = config.get('Bot', 'servername')
if config.has_option('Bot', 'channel'):
	channel = config.get('Bot', 'channel')
if config.has_option('Bot', 'nickname'):
	nickname = config.get('Bot', 'nickname')

bot = False

if channel != '' and servername != '' and nickname != '':
	bot = IrcBot(servername, nickname, port)
	bot.connect()
	bot.join(channel)
else:
	print 'Could not start IRC Bot.  You must supply a servername, channel, and nickname.'

def onIrcMsg(bot, username, msg):
	sbserver.message('(Remote User) %s: %s' % (username, msg))

def onPlayerActive(cn):
	bot.privMsg(channel, 'Player %s (%i) has joined' % (sbserver.playerName(cn), cn))

def onPlayerDisconnect(cn):
	bot.privMsg(channel, 'Player %s (%i) has disconnected' % (sbserver.playerName(cn), cn))

def onMsg(cn, text):
	bot.privMsg(channel, '%s (%i): %s' % (sbserver.playerName(cn), cn, text))

def onTeamMsg(cn, text):
	bot.privMsg(channel, '%s (%i) (Team): %s' % (sbserver.playerName(cn), cn, text))

event_abilities = {
	'player_active': ('player_active', onPlayerActive),
	'player_disconnect': ('player_disconnect', onPlayerDisconnect),
	'message': ('player_message', onMsg),
	'message_team': ('player_message_team', onTeamMsg) }

if bot:
		for key in event_abilities.keys():
			if config.has_option('Abilities', key) and config.get('Abilities', key) == 'yes':
				ev = event_abilities[key]
				sbevents.registerEventHandler(ev[0], ev[1])

		if config.has_option('Abilities', 'message_gateway') and config.get('Abilities', 'message_gateway') == 'yes':
			bot.msg_handlers.append(onIrcMsg)

