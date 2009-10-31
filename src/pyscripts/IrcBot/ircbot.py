import sbserver
from ConfigParser import NoOptionError
from xsbs.settings import PluginConfig
from xsbs.events import registerServerEventHandler
from xsbs.timers import addTimer
from xsbs.colors import red, green
import asyncore, socket
import asynirc
import logging

config = PluginConfig('ircbot')
channel = config.getOption('Config', 'channel', '#xsbs-newserver')
servername = config.getOption('Config', 'servername', 'irc.gamesurge.net')
nickname = config.getOption('Config', 'nickname', 'xsbs-newbot')
port = int(config.getOption('Config', 'port', '6667'))
part_message = config.getOption('Config', 'part_message', 'QUIT :XSBS - eXtensible SauerBraten Server')
msg_gw = config.getOption('Abilities', 'message_gateway', 'yes') == 'yes'
try:
	ipaddress = config.getOption('Config', 'ipaddress', None, False)
except NoOptionError:
	ipaddress = None

class ServerBot(asynirc.IrcClient):
	def __init__(self, serverinfo, clientinfo):
		asynirc.IrcClient.__init__(self, serverinfo, clientinfo)

bot = ServerBot(
	(servername, 6667),
	(nickname, nickname.lower(), 'localhost', 'localhost', nickname))
if(ipaddress):
	bot.ip_address = ipaddress
bot.join(channel)
bot.doConnect()

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

def onAuthSucceed(cn, name):
	bot.message('\x03AUTH\x03             %s authenticated as %s' % (sbserver.playerName(cn), name))

def onGainMaster(cn):
	bot.message('\x037MASTER          \x03%s gained master' % sbserver.playerName(cn), channel)

def onGainAdmin(cn):
	bot.message('\x037ADMIN           \x03%s gained admin' % sbserver.playerName(cn), channel)

def onAuth(cn, authname):
	bot.message('\x037AUTH            \x03%s has authenticated as %s' % (sbserver.playerName(cn), authname), channel)

def onReleaseAdmin(cn):
	bot.message('\x037ADMIN RELINQ    \x03%s released admin' % sbserver.playerName(cn), channel)

def onReleaseMaster(cn):
	bot.message('\x037MASTER RELINQ   \x03%s released master' % sbserver.playerName(cn), channel)

def onBan(cn, seconds, reason):
	bot.message('\x0313BAN             \x03%s banned for %i for %s' % (sbserver.playerName(cn), seconds, reason), channel)

def onSpectated(cn):
	bot.message('\x0314SPECTATED       \x03%s became a spectator' % sbserver.playerName(cn), channel)

def onUnSpectated(cn):
	bot.message('\x0314UNSPECTATED     \x03%s unspectated' % sbserver.playerName(cn), channel)

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
	'auth_success': ('player_auth_succeed', onAuthSucceed),
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

