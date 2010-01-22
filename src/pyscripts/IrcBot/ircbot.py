from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from xsbs.settings import PluginConfig, NoOptionError
from xsbs.events import registerServerEventHandler
from xsbs.timers import addTimer

import sbserver

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
	def connectionLost(self, reason):
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

class IrcBotFactory(protocol.ClientFactory):
	protocol = IrcBot
	def __init__(self, nickname, channels):
		self.nickname = nickname
		self.channels = channels
		self.bots = []
		self.reconnect_count = 0
	def doConnect(self):
		reactor.connectTCP(servername, int(port), factory)
	def doReconnect(self):
		if self.reconnect_count < 5:
			self.reconnect_count += 1
			self.doConnect()
	def signedOn(self, bot):
		if bot not in self.bots:
			self.bots.append(bot)
	def signedOut(self, bot):
		if bot in self.bots:
			self.bots.remove(bot)
			addTimer(5000, self.doReconnect, ())
	def broadcast(self, message):
		for bot in self.bots:
			bot.broadcast(message)

factory = IrcBotFactory(nickname, [channel])

event_abilities = {
	'player_active': ('player_connect', lambda x: factory.broadcast(
		'\x032CONNECT\x03        %s (\x037 %i \x03)' % (sbserver.playerName(x), x))),
	'player_disconnect': ('player_disconnect', lambda x: factory.broadcast(
		'\x032DISCONNECT\x03     %s (\x037 %i \x03)' % (sbserver.playerName(x), x))),
	'message': ('player_message', lambda x, y: factory.broadcast(
		'\x033MESSAGE\x03        %s (\x037 %i \x03): %s' % (sbserver.playerName(x), x, y))),
	'map_change': ('map_changed', lambda x, y: factory.broadcast(
		'\x038MAP CHANGE\x03     %s (%s)' % (x, sbserver.modeName(y)))),
	'gain_admin': ('player_claimed_admin', lambda x: factory.broadcast(
		'\x036CLAIM ADMIN\x03    %s (\x037 %i \x03)' % (sbserver.playerName(x), x))),
	'gain_master': ('player_claimed_master', lambda x: factory.broadcast(
		'\x036CLAIM MASTER\x03   %s (\x037 %i \x03)' % (sbserver.playerName(x), x))),
	'auth': ('player_auth_succeed', lambda x, y: factory.broadcast(
		'\x036AUTH\x03           %s (\x037 %i \x03) as %s@sauerbraten.org' % (sbserver.playerName(x), x, y))),
	'relinquish_admin': ('player_released_admin', lambda x: factory.broadcast(
		'\x036RELINQ ADMIN\x03   %s (\x037 %i \x03)' % (sbserver.playerName(x), x))),
	'relinquish_master': ('player_released_master', lambda x: factory.broadcast(
		'\x036RELINQ MASTER\x03  %s (\x037 %i \x03)' % (sbserver.playerName(x), x))),
}

for key in event_abilities.keys():
	if config.getOption('Abilities', key, 'no') == 'yes':
		ev = event_abilities[key]
		registerServerEventHandler(ev[0], ev[1])


