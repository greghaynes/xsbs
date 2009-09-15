import sbserver
from xsbs.settings import PluginConfig
from xsbs.colors import red, colordict
from xsbs.events import registerServerEventHandler, registerPolicyEventHandler, execLater
from xsbs.commands import registerCommandHandler
import time, string

banned_ips = {}

config = PluginConfig('bans')
ban_command = config.getOption('Config', 'ban_command', 'ban')
default_ban_length = config.getOption('Config', 'default_ban_time', 3600)
ban_message = config.getOption('Config', 'message', 'Banning $name for $seconds seconds for ${red}${reason}')
ban_message = string.Template(ban_message)
default_reason = config.getOption('Config', 'default_reason', 'unspecified reason')
del config

def onBanCmd(cn, text):
	sp = text.split(' ')
	try:
		if sbserver.playerPrivilege(cn) == 0:
			sbserver.playerMessage(cn, red('Insufficient privileges.'))
			return
		tcn = int(sp[0])
		try:
			ip = sbserver.playerIpLong(tcn)
		except ValueEror:
			sbserver.message(cn, red('Invalid cn'))
			return
		reason = ''
		length = 0
		if len(sp) >= 3:
			reason = sp[2]
		else:
			reason = default_reason
		if len(sp) >= 2:
			length = int(sp[1])
		else:
			length = int(default_ban_length)
		ban(cn, length, reason)
	except (ValueError, KeyError):
		sbserver.playerMessage(cn, red('Usage: #ban <cn> (duration) (reason)'))

def ban(cn, seconds, reason):
	ip = sbserver.playerIpLong(cn)
	msg = ban_message.substitute(colordict, name=sbserver.playerName(cn), seconds=seconds, reason=reason)
	sbserver.message(msg)
	expiration = time.time() + seconds
	if banned_ips.has_key(ip):
		if banned_ips[ip] > expiration:
			execLater(sbserver.playerKick, (cn,))
			return
	banned_ips[ip] = expiration
	execLater(sbserver.playerKick, (cn,))

def allowClient(cn):
	ip = sbserver.playerIpLong(cn)
	if banned_ips.has_key(ip):
		expiration = banned_ips[ip]
		if time.time() >= expiration:
			banned_ips.pop(ip)
			return True
		return False
	return True

def init():
	registerPolicyEventHandler("allow_connect", allowClient)
	registerCommandHandler('ban', onBanCmd)
	registerServerEventHandler("player_ban", ban)

init()
