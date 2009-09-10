import sbevents, sbserver
from settings import PluginConfig
import socket

config = PluginConfig('ircbot')
channel = config.getOption('Config', 'channel', '#xsbs-newserver')
servername = config.getOption('Config', 'servername', 'irc.gamesurge.net')
nickname = config.getOption('Config', 'nickname', 'xsbs-newbot')
port = int(config.getOption('Config', 'port', '6667'))
del config

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
		try:
			self.buff = self.socket.recv(4096)
			self.socket.send('NICK %s\r\n' % self.nickname)
			self.socket.send('USER %s %s %s :%s\r\n' % (self.nickname, self.nickname, self.nickname, self.nickname))
		except:
			print 'Error connecting to IRC server.'
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
		try:
			self.socket.send('PRIVMSG %s :%s\r\n' % (user, message))
		except:
			print 'Error sending IRC message.'
	def processData(self):
		try:
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
					user = line[0].split('!')[0][1:]
					text = line[3][1:]
					if len(line) >= 4:
						for t in line[4:]:
							text += ' '
							text += t
					for handler in self.msg_handlers:
						handler(self, user, text)
		except:
			print 'Error processing data from IRC.'

bot = IrcBot(servername, nickname, port)
bot.connect()
bot.join(channel)

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

