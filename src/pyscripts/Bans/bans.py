import sbserver, sbevents, sbtools
from settings import PluginConfig
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
			sbserver.playerMessage(cn, sbtools.red('Insufficient privileges.'))
			return
		tcn = int(sp[0])
		ip = sbserver.playerIpLong(tcn)
		if not ip:
			sbserver.message(cn, 'Invalid cn')
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
		sbserver.playerMessage(cn, sbtools.red('Usage: #ban <cn> (duration) (reason)'))

def ban(cn, seconds, reason):
	ip = sbserver.playerIpLong(cn)
	msg = ban_message.substitute(sbtools.colordict, name=sbserver.playerName(cn), seconds=seconds, reason=reason)
	sbserver.message(msg)
	expiration = time.time() + seconds
	if banned_ips.has_key(ip):
		if banned_ips[ip] > expiration:
			sbserver.playerKick(cn)
			return
	banned_ips[ip] = expiration
	sbevents.sbExec(sbserver.playerKick, (cn,))

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
	sbevents.registerCommandHandler('ban', onBanCmd)
	sbevents.registerEventHandler("player_ban", ban)

init()
