import sbserver
from ConfigParser import NoOptionError
from xsbs.settings import PluginConfig
from xsbs.events import registerServerEventHandler
from xsbs.timers import addTimer
from xsbs.colors import red, green
import asyncore, socket
import logging

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
		logging.warning('Connection closed')
		logging.warning('Reconnecting in 5 seconds')
		self.connect_count += 1
		if self.connect_count >= 5:
			logging.warning('Connect failed 5 times.  Quitting.')
		self.close()
	def handle_connect(self):
		logging.info('Conneced')
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
		msg = '%i clients: %i players, %i spectators Playing %s on %s' % (len(clients), len(players), len(clients) - len(players), sbserver.modeName(sbserver.gameMode()), sbserver.mapName())
		self.privMsg(channel, msg)
	def handle_privmsg(self, sender, message):
		if message[0] == '!':
			try:
				self.msgcommands[message[1:]](sender, message)
			except KeyError:
				self.privMsg(channel, 'Invalid command')
		else:
			sbserver.message((red('Remote User') + green(' %s') + ': %s') % (sender, message))
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
				logging.warning('IRC Bot: Nickname is in use!')
				self.nickname = self.nickname + '1'
				logging.warning('IRC Bot: Using %s' % self.nickname)
				self.sendNick()

bot = IrcBot(servername, nickname, port)
bot.join(channel)

def onPlayerConnect(cn):
	bot.privMsg(channel, '\x032CONNECT         \x03Player %s (%i) has joined' % (sbserver.playerName(cn), cn))

def onPlayerDisconnect(cn):
	bot.privMsg(channel, '\x032DISCONNECT      \x03Player %s (%i) has disconnected' % (sbserver.playerName(cn), cn))

def onMsg(cn, text):
	bot.privMsg(channel, '\x033MESSAGE         \x03%s (%i): %s' % (sbserver.playerName(cn), cn, text))

def onTeamMsg(cn, text):
	bot.privMsg(channel, '\x033MESSAGE (TEAM)  \x03%s (%i) (Team): %s' % (sbserver.playerName(cn), cn, text))

def onMapChange(map, mode):
	bot.privMsg(channel, '\x035MAP CHANGE      \x03%s (%s)' % (map, sbserver.modeName(mode)))

def onGainMaster(cn):
	bot.privMsg(channel, '\x037MASTER          \x03%s gained master' % sbserver.playerName(cn))

def onGainAdmin(cn):
	bot.privMsg(channel, '\x037ADMIN           \x03%s gained admin' % sbserver.playerName(cn))

def onAuth(cn, authname):
	bot.privMsg(channel, '\x037AUTH            \x03%s has authenticated as %s' % (sbserver.playerName(cn), authname))

def onReleaseAdmin(cn):
	bot.privMsg(channel, '\x037ADMIN RELINQ    \x03%s released admin' % sbserver.playerName(cn))

def onReleaseMaster(cn):
	bot.privMsg(channel, '\x037MASTER RELINQ   \x03%s released master' % sbserver.playerName(cn))

def onBan(cn, seconds, reason):
	bot.privMsg(channel, '\x0313BAN             \x03%s banned for %i for %s' % (sbserver.playerName(cn), seconds, reason))

def onSpectated(cn):
	bot.privMsg(channel, '\x0314SPECTATED       \x03%s became a spectator' % sbserver.playerName(cn))

def onUnSpectated(cn):
	bot.privMsg(channel, '\x0314UNSPECTATED     \x03%s unspectated' % sbserver.playerName(cn))

def onReload():
	bot.quit()

def onStop():
	bot.quit()

event_abilities = {
	'player_active': ('player_connect', onPlayerConnect),
	'player_disconnect': ('player_disconnect', onPlayerDisconnect),
	'message': ('player_message', onMsg),
	'message_team': ('player_message_team', onTeamMsg),
	'map_change': ('map_changed', onMapChange),
	'gain_admin': ('player_gained_admin', onGainAdmin),
	'gain_master': ('player_gained_master', onGainMaster),
	'auth': ('player_auth_master', onAuth),
	'relinquish_admin': ('player_relinq_admin', onReleaseAdmin),
	'relinquish_master': ('player_relinq_master', onReleaseMaster),
	'ban': ('player_banned', onBan),
	'spectate': ('player_spectated', onSpectated),
	'unspectate': ('player_unspectated', onUnSpectated),
}

for key in event_abilities.keys():
	if config.getOption('Abilities', key, 'no') == 'yes':
		ev = event_abilities[key]
		registerServerEventHandler(ev[0], ev[1])
del config

registerServerEventHandler('reload', onReload)
registerServerEventHandler('server_stop', onStop)

