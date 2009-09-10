import sbserver, sbevents
from settings import loadConfigFile
import time, string
from ConfigParser import ConfigParser

banned_ips = {}
ban_command = 'ban'
default_ban_length = 3600
ban_message = string.Template('Banning $name for $seconds seconds for $reason.')
default_reason = 'unspecified reason'

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

config = loadConfigFile('bans')
if config.has_option('Config', 'ban_command'):
	ban_command = config.get('Config', 'ban_command')
if config.has_option('Config', 'default_ban_length'):
	default_ban_length = config.get('Config', 'default_ban_length')
if config.has_option('Config', 'ban_message'):
	ban_message = config.get('Config', 'ban_message')
if config.has_option('Config', 'default_reason'):
	default_reason = config.get('Config', 'default_reason')
del config

init()
