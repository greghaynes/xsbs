import sbserver
from xsbs.settings import PluginConfig
from xsbs.events import registerServerEventHandler
import asyncore, socket

config = PluginConfig('ircbot')
channel = config.getOption('Config', 'channel', '#xsbs-newserver')
servername = config.getOption('Config', 'servername', 'irc.gamesurge.net')
nickname = config.getOption('Config', 'nickname', 'xsbs-newbot')
port = int(config.getOption('Config', 'port', '6667'))

class IrcBot(asyncore.dispatcher):
	def __init__(self, servername, nickname, port=6667):
		asyncore.dispatcher.__init__(self)
		self.servername = servername
		self.nickname = nickname
		self.port = port
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.isConnected = False
		self.channels = []
		self.msg_handlers = []
		self.buff = ''
		self.writebuff = 'NICK %s\r\n' % self.nickname
		self.writebuff += 'USER %s %s %s :%s\r\n' % (self.nickname, self.nickname, self.nickname, self.nickname)
		self.connect((self.servername, self.port))
	def __del__(self):
		self.close()
	def handle_connect(self):
		pass
	def handle_write(self):
		sent = self.send(self.writebuff)
		self.writebuff = self.writebuff[sent:]
	def writeable(self):
		return len(self.writebuff) > 0
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
				for handler in self.msg_handlers:
					handler(self, user, text)

bot = IrcBot(servername, nickname, port)
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

for key in event_abilities.keys():
	if config.getOption('Abilities', key, 'no') == 'yes':
		ev = event_abilities[key]
		registerServerEventHandler(ev[0], ev[1])
if config.getOption('Abilities', 'message_gateway', 'no') == 'yes':
	bot.msg_handlers.append(onIrcMsg)
del config

