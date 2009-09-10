import sbserver, sbevents
from settings import PluginConfig
import time, string

banned_ips = {}

config = PluginConfig('bans')
ban_command = config.getOption('Config', 'ban_command', 'ban')
default_ban_length = config.getOption('Config', 'default_ban_time', 3600)
ban_message = config.getOption('Config', 'message', 'Banning $name for $seconds seconds for $red$reason$white.')
ban_message = string.Template(ban_message)
default_reason = config.getOption('Config', 'default_reason', 'unspecified reason')
del config

def onMessage(cn, text):
	sp = text.split(' ')
	if len(sp) >=2 and sp[0] == ban_command and sp[1]:
		if sbserver.playerPrivilege(cn) == 0:
			sbserver.playerMessage(cn, 'Insufficient privileges.')
			return
		tcn = int(sp[1])
		ip = sbserver.playerIpLong(tcn)
		if not ip:
			sbserver.message(cn, 'Invalid cn')
			return
		reason = ''
		length = 0
		if len(sp) >= 4:
			reason = sp[3]
			length = int(sp[2])
		elif len(sp) == 3:
			reason = default_reason
			length = int(sp[2])
		else:
			return
		ban(cn, length, reason)

def ban(cn, seconds, reason):
	ip = sbserver.playerIpLong(cn)
	msg = ban_message.substitute(name=sbserver.playerName(cn), seconds=seconds, reason=reason)
	sbserver.message(msg)
	expiration = time.time() + seconds
	if banned_ips.has_key(ip):
		if banned_ips[ip] > expiration:
			sbserver.playerKick(cn)
			return
	banned_ips[ip] = expiration
	sbserver.playerKick(cn)

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
	sbevents.registerPolicyEventHandler("allow_connect", allowClient)
	sbevents.registerEventHandler("player_command", onMessage)
	sbevents.registerEventHandler("player_ban", ban)

init()
