import sbserver
from ConfigParser import NoOptionError
from xsbs.settings import PluginConfig
from xsbs.events import registerServerEventHandler
from xsbs.timers import addTimer
from xsbs.colors import red, green, colordict
from xsbs.ui import info, error
from xsbs.commands import commandHandler, UsageError
from xsbs.players import clientCount
from UserPrivilege.userpriv import masterRequired, adminRequired
import irc
import string
import logging

config = PluginConfig('ircbot')
enable = config.getOption('Config', 'enable', 'yes') == 'yes'
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

# This decode is borrowed from Phenny, under same license as irc.py
def decode(bytes): 
	try: text = bytes.decode('utf-8')
	except UnicodeDecodeError: 
		try: text = bytes.decode('iso-8859-1')
		except UnicodeDecodeError: 
			text = bytes.decode('cp1252')
	return text

class Bot(irc.Bot):
	def __init__(self, nick, name, channel):
		irc.Bot.__init__(self, nick, name, (channel,))
		self.event_handlers = { '251': self.handle_mode,
			'PRIVMSG': self.handle_privmsg,
			'433': self.handle_nick_in_use }
		self.connect_complete = False
	def dispatch(self, origin, args):
		bytes, event, args = args[0], args[1], args[2:]
		text = decode(bytes)
		try:
			self.event_handlers[event](origin, event, args, bytes)
		except KeyError:
			pass
	def handle_mode(self, origin, event, args, bytes):
		if not self.connect_complete:
			self.connect_complete = True
			self.handle_complete_connect()
	def handle_privmsg(self, origin, event, args, bytes):
		if args[0] in self.channels:
			if bytes[0] in '.!#@':
				cmd_args = bytes.split(' ', 1)
				self.handle_command(args, origin, cmd_args[0][1:], cmd_args[1])
			else:
				sbserver.message(irc_msg_temp.substitute(colordict, name=origin.nick, message=bytes))
	def handle_nick_in_use(self, origin, event, args, bytes):
		logging.error('Nickname already in use')
	def handle_command(self, origin, command, bytes):
		pass
	def handle_complete_connect(self):
		for chan in self.channels:
			self.write(('JOIN', chan))
	def broadcast(self, message):
		if not self.connect_complete:
			return
		for chan in self.channels:
			self.msg(chan, message)

irc_msg_temp = string.Template(irc_msg_temp)
status_message = string.Template(status_message)

bot = Bot(nickname, 'xsbs', channel)
if enable:
	bot.run(servername, port)

event_abilities = {
	'player_active': ('player_connect', lambda x: bot.broadcast(
		'CONNECT        %s (%i)' % (sbserver.playerName(x), x))),
	'player_disconnect': ('player_disconnect', lambda x: bot.broadcast(
		'DISCONNECT     %s (%i)' % (sbserver.playerName(x), x))),
	'message': ('player_message', lambda x, y: bot.broadcast(
		'MESSAGE        %s (%i): %s' % (sbserver.playerName(x), x, y))),
	'map_change': ('map_changed', lambda x, y: bot.broadcast(
		'MAP CHANGE     %s (%s)' % (map, sbserver.modeName(mode)))),
	'gain_admin': ('player_claimed_admin', lambda x: bot.broadcast(
		'CLAIM ADMIN    %s (%i)' % (sbserver.playerName(x), x))),
	'gain_master': ('player_claimed_master', lambda x: bot.broadcast(
		'CLAIM MASTER   %s (%i)' % (sbserver.playerName(x), x))),
	'auth': ('player_auth_succeed', lambda x, y: bot.broadcast(
		'AUTH           %s (%i) as %s@sauerbraten.org' % (sbserver.playerName(x), x, y))),
	'relinquish_admin': ('player_released_admin', lambda x: bot.broadcast(
		'RELINQ ADMIN   %s (%i)' % (sbserver.playerName(x), x))),
	'relinquish_master': ('player_released_master', lambda x: bot.broadcast(
		'RELINQ MASTER  %s (%i)' % (sbserver.playerName(x), x))),
}

for key in event_abilities.keys():
	if config.getOption('Abilities', key, 'no') == 'yes':
		ev = event_abilities[key]
		registerServerEventHandler(ev[0], ev[1])
del config

