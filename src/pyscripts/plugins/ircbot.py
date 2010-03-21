from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from xsbs.colors import colordict
from xsbs.settings import loadPluginConfig, NoOptionError
from xsbs.events import registerServerEventHandler
from xsbs.timers import addTimer
from xsbs.server import message

import sbserver

import string

config = {
	'Main': {
		'enable': 'no',
		'part_message': 'XSBS - eXtensible SauerBraten Server',
		'ipaddress': '0',
		},
	'Connection': {
		'server': 'irc.gamesurge.net',
		'port': '6667',
		'nickname': 'xsbs-newbot',
		'channel': '#xsbs-newserver'
		},
	'Features': {
		'message_gateway': 'yes',
		'player_disconnect': 'yes',
		'player_connect': 'yes',
		'message': 'yes',
		'map_change': 'yes',
		'gain_admin': 'yes',
		'gain_master': 'yes',
		'relinquish_master': 'yes',
		'relinquish_admin': 'yes'
		},
	'Alerts': {
		'player_connect': 'yes',
		'player_disconnect': 'yes',
		'message': 'yes',
		'team_message': 'no',
		'map_change': 'yes',
		'gain_admin': 'yes',
		'gain_master': 'yes',
		'auth': 'yes',
		'relinquish_master': 'yes',
		'relinquish_admin': 'yes'
		},
	'Templates': {
		'irc_message': '${grey}${channel} ${blue}${name}${white}: ${message}',
		'status_message': '${num_clients} clients on map ${map_name}',

		'player_connect': '${magenta}${name}${white} connected',
		'player_disconnect': '${magenta}${name}${white} disconnected',
		'message': '${magenta}${name}${white}: ${message}',
		'map_change': 'map change: ${map}',
		'gain_admin': '${magenta}${name}${white} has claimed admin',
		'gain_master': '${magenta}${name}${white} has claimed master',
		'auth': '${magenta}${name}${white} has authenticated as ${authname}@sauerbraten.org',
		'relinquish_admin': '${magenta}${white} has relinquished admin',
		'relinquish_master': '${magenta}${white} has relinquished master'
		}
	}

irccolordict = {
		'black': '\x030',
		'red': '\x031',
		'green': '\x032',
		'yellow': '\x033',
		'blue': '\x034',
		'magenta': '\x035',
		'cyan': '\x036',
		'white': '\x037',
		'default': '\x039',

		'bgblack': '\x040',
		'bgred': '\x041',
		'bggreen': '\x042',
		'bgyellow': '\x043',
		'bgblue': '\x044',
		'bgmagenta': '\x045',
		'bgcyan': '\x046',
		'bgwhite': '\x047',
		'bgdefault': '\x049',
	}

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
	def privmsg(self, user, channel, msg):
		if channel == config['Connection']['channel']:
			user = user.split('!', 1)[0]
			message(config['Templates']['irc_message'].substitute(colordict, channel=channel, name=user, message=msg))
		
class IrcBotFactory(protocol.ClientFactory):
	protocol = IrcBot
	def __init__(self, nickname, channels):
		self.nickname = nickname
		self.channels = channels
		self.bots = []
		self.reconnect_count = 0
	def doConnect(self):
		if ipaddress == '0':
			reactor.connectTCP(config['Connection']['server'], int(config['Connection']['port']), factory)
		else:
			reactor.connectTCP(config['Connection']['server'], int(config['Connection']['port']), factory, 30, (config['Connection']['ipaddress'], 0))
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

event_abilities = {
	'player_connect': ('player_connect', lambda x: factory.broadcast('%s (\x037 %i \x03) \x032Connected\x03' % (sbserver.playerName(x), x))),
	'player_disconnect': ('player_disconnect', lambda x: factory.broadcast('%s (\x037 %i \x03) \x032Disconnected\x03' % (sbserver.playerName(x), x))),
	'message': ('player_message', lambda x, y: factory.broadcast('%s (\x037 %i \x03): %s' % (sbserver.playerName(x), x, y))),
	'map_change': ('map_changed', lambda x, y: factory.broadcast('\x038Map changed to:\x03 %s (%s)' % (x, sbserver.modeName(y)))),
	'gain_admin': ('player_claimed_admin', lambda x: factory.broadcast('%s (\x037 %i \x03) \x036Has claimed admin\x03' % (sbserver.playerName(x), x))),
	'gain_master': ('player_claimed_master', lambda x: factory.broadcast('%s (\x037 %i \x03) \x036Has claimed master\x03' % (sbserver.playerName(x), x))),
	'auth': ('player_auth_succeed', lambda x, y: factory.broadcast('%s (\x037 %i \x03) has authenticated as\x036 %s@sauerbraten.org\x03' % (sbserver.playerName(x), x, y))),
	'relinquish_admin': ('player_released_admin', lambda x: factory.broadcast('%s (\x037 %i \x03) \x036Has relinquished admin\x03' % (sbserver.playerName(x), x))),
	'relinquish_master': ('player_released_master', lambda x: factory.broadcast('%s (\x037 %i \x03) \x036Has relinquished master\x03' % (sbserver.playerName(x), x))),
}

factory = IrcBotFactory(config['Connection']['nickname'], [config['Connection']['channel']])

def init():
	loadPluginConfig(config, 'IrcBot')
	config['Templates']['irc_message'] = string.Template(config['Templates']['irc_message'])
	if config['Main']['enable'] == 'yes':
		factory.doConnect()
		for key in event_abilities.keys():
			if config['Features'][key] == 'yes':
				ev = event_abilities[key]
				registerServerEventHandler(ev[0], ev[1])

init()

