from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from xsbs.settings import PluginConfig, NoOptionError
from xsbs.events import registerServerEventHandler

import string

config = PluginConfig('ircbot')
enable = config.getOption('Config', 'enable', 'no') == 'yes'
channel = config.getOption('Config', 'channel', '#xsbs-newserver')
servername = config.getOption('Config', 'servername', 'irc.gamesurge.net')
nickname = config.getOption('Config', 'nickname', 'xsbs-newbot')
port = int(config.getOption('Config', 'port', '6667'))
part_message = config.getOption('Config', 'part_message', 'XSBS - eXtensible SauerBraten Server')
msg_gw = config.getOption('Abilities', 'message_gateway', 'yes') == 'yes'
irc_msg_temp = config.getOption('Templates', 'irc_message', '${white}(${blue}IRC${white}) ${red}${name}${white}: ${message}')
status_message = config.getOption('Templates', 'status_message', '${num_clients} clients on map ${map_name}')
try:
	ipaddress = config.getOption('Config', 'ipaddress', None, False)
except NoOptionError:
	ipaddress = None

class IrcBot(irc.IRCClient):
	def connectionMade(self):
		self.nickname = self.factory.nickname
		irc.IRCClient.connectionMade(self)
		self.joined_channels = []
	def signedOn(self):
		for channel in self.factory.channels:
			self.join(channel)
		self.factory.signedOn(self)
	def connectionLost(self):
		self.factory.signedOut(self)
	def joined(self, channel):
		if channel not in self.joined_channels:
			self.joined_channels.append(channel)
	def left(self, channel):
		if channel in self.joined_channels:
			self.joined_channels.remove(channel)
	def broadcast(self, message):
		for channel in self.joined_channels:
			self.say(channel, message)

class ServerEventDispatcher(object):
	def __init__(self, factory):
		self.factory = factory
	def broadcast(self, message):
		for bot in self.factory.bots:
			bot.broadcast(message)
	def playerConnected(self, cn):
		self.broadcast('User connected')

class IrcBotFactory(protocol.ClientFactory):
	protocol = IrcBot
	def __init__(self, nickname, channels):
		self.nickname = nickname
		self.channels = channels
		self.event_dispatch = ServerEventDispatcher(self)
		self.bots = []
	def signedOn(self, bot):
		if bot not in self.bots:
			self.bots.append(bot)
	def signedOut(self, bot):
		if bot in self.bots:
			self.bots.remove(bot)

factory = IrcBotFactory(nickname, [channel])

registerServerEventHandler('player_connect', lambda x: factory.event_dispatch.playerConnected(x))

reactor.connectTCP(servername, int(port), factory)

