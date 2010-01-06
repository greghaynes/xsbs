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
import asyncore, socket
import asynirc
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

irc_msg_temp = string.Template(irc_msg_temp)
status_message = string.Template(status_message)

class ServerBot(asynirc.IrcClient):
	def __init__(self, serverinfo, clientinfo, msg_gw):
		asynirc.IrcClient.__init__(self, serverinfo, clientinfo)
		self.msg_gw = msg_gw
		self.do_reconnect = True
		self.reconnect_count = 0
		self.part_message = part_message
	def reconnect(self):
		if self.is_connected == True:
			return
		if self.reconnect_count >= 5:
			logging.error('Max recconect failures (5) occoured.')
		else:
			self.reconnect_count += 1
			self.doConnect()
	def handle_connect(self):
		self.reconnect_count = 0
		asynirc.IrcClient.handle_connect(self)
	def handle_close(self):
		asynirc.IrcClient.handle_close(self)
		if self.do_reconnect:
			addTimer(20000, self.reconnect)
	def handle_privmsg(self, who, to, message):
		if message[0] in '.!@#':
			command = message.split(' ')[0].strip()[1:]
			message = message[len(command)+1:].strip()
			self.handle_msg_command(who, to, command, message)
		elif self.msg_gw and to[0] == channel:
			name = who.split('!', 1)[0]
			sbserver.message(irc_msg_temp.substitute(colordict, name=name, message=message, channel=to))
	def handle_msg_command(self, who, to, command, message):
		if command == 'status':
			message = status_message.substitute(num_clients=clientCount(), map_name=sbserver.mapName())
			self.message(message, channel)
	def quit(self):
		self.do_reconnect = False
		asynirc.IrcClient.quit(self)

bot = ServerBot(
	(servername, 6667),
	(nickname, nickname.lower(), 'localhost', 'localhost', nickname),
	msg_gw)
if(ipaddress):
	bot.ip_address = ipaddress
bot.join(channel)

if enable:
	bot.doConnect()

@commandHandler('ircbot')
@adminRequired
def ircbotCmd(cn, args):
	'''@description Enable or disable the irc bot
	   @usage <on/off>'''
	if args == 'off':
		bot.quit()
		sbserver.playerMessage(cn, info('Irc bot disabled'))
	elif args == 'on':
		bot.doConnect()
		sbserver.playerMessage(cn, info('Irc bot enabled'))
	else:
		raise UsageError('off/on')

def onPlayerConnect(cn):
	bot.message('\x032CONNECT         \x03Player %s (%i) has joined' % (sbserver.playerName(cn), cn), channel)

def onPlayerDisconnect(cn):
	bot.message('\x032DISCONNECT      \x03Player %s (%i) has disconnected' % (sbserver.playerName(cn), cn), channel)

def onMsg(cn, text):
	bot.message('\x033MESSAGE\x03         %s (%i): %s' % (sbserver.playerName(cn), cn, text), channel)

def onTeamMsg(cn, text):
	bot.message('\x033MESSAGE (TEAM)\x03  %s (%i) (Team): %s' % (sbserver.playerName(cn), cn, text), channel)

def onMapChange(map, mode):
	bot.message('\x035MAP CHANGE\x03      %s (%s)' % (map, sbserver.modeName(mode)), channel)

def onGainMaster(cn):
	bot.message('\x037MASTER\x03          %s gained master' % sbserver.playerName(cn), channel)

def onGainAdmin(cn):
	bot.message('\x037ADMIN\x03           %s gained admin' % sbserver.playerName(cn), channel)

def onAuth(cn, authname):
	bot.message('\x037AUTH\x03            %s has authenticated as %s' % (sbserver.playerName(cn), authname), channel)

def onReleaseAdmin(cn):
	bot.message('\x037ADMIN RELINQ\x03    %s released admin' % sbserver.playerName(cn), channel)

def onReleaseMaster(cn):
	bot.message('\x037MASTER RELINQ\x03   %s released master' % sbserver.playerName(cn), channel)

def onBan(cn, seconds, reason):
	bot.message('\x0313BAN\x03            %s banned for %i for %s' % (sbserver.playerName(cn), seconds, reason), channel)

def onSpectated(cn):
	bot.message('\x0314SPECTATED\x03      %s became a spectator' % sbserver.playerName(cn), channel)

def onUnSpectated(cn):
	bot.message('\x0314UNSPECTATED\x03    %s unspectated' % sbserver.playerName(cn), channel)

def onNameChanged(cn, new_name):
	bot.message('\x0314NAME CHANGE\x03    %s (%i) changed name' % (new_name, cn), channel)

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
	'gain_admin': ('player_claimed_admin', onGainAdmin),
	'gain_master': ('player_claimed_master', onGainMaster),
	'auth': ('player_auth_succeed', onAuth),
	'relinquish_admin': ('player_released_admin', onReleaseAdmin),
	'relinquish_master': ('player_released_master', onReleaseMaster),
	'ban': ('player_banned', onBan),
	'spectate': ('player_spectated', onSpectated),
	'unspectate': ('player_unspectated', onUnSpectated),
	'name_change': ('player_name_changed', onNameChanged),
}

for key in event_abilities.keys():
	if config.getOption('Abilities', key, 'no') == 'yes':
		ev = event_abilities[key]
		registerServerEventHandler(ev[0], ev[1])
del config

registerServerEventHandler('reload', onReload)
registerServerEventHandler('server_stop', onStop)

