from elixir import session

from xsbs.settings import loadPluginConfig
from xsbs.colors import red, colordict
from xsbs.ui import insufficientPermissions, error, info
from xsbs.commands import commandHandler, UsageError, ArgumentValueError
from xsbs.events import triggerServerEvent, eventHandler, policyHandler, execLater
from xsbs.ban import ban, isIpBanned, isNickBanned, Ban
from xsbs.net import ipLongToString, ipStringToLong
from xsbs.players import masterRequired, player
from xsbs.server import message as serverMessage

import time, string
import logging

config = {
	'Main': {
		'command': 'ban',
		'default_length': '3600',
		'default_reason': 'unspecified reason',
		'kick_message': '${green}${name}${white} was ${red}kicked${white} from server',
		}
	}
def init():
	loadPluginConfig(config, 'Bans')
	config['Main']['kick_message'] = string.Template(config['Main']['kick_message'])

init()

@commandHandler('ban')
@masterRequired
def onBanCmd(p, text):
	'''@description Ban user from server
	   @usage <seconds> (reason)'''
	sp = text.split(' ')
	try:
		tcn = int(sp[0])
		ip = p.ipLong()
		reason = ''
		length = 0
		if len(sp) >= 3:
			reason = sp[2]
		else:
			reason = config['Main']['default_reason']
		if len(sp) >= 2:
			length = int(sp[1])
		else:
			length = int(config['Main']['default_length'])
		ban(tcn, length, reason, p.cn)
	except (ValueError, KeyError):
		raise UsageError('cn (duration) (reason)')

@commandHandler('recentbans')
@masterRequired
def onRecentBans(p, args):
	'''@description Recently added bans
	   @usage'''
	if args != '':
		raise UsageError()
	else:
		recent = session.query(Ban).order_by(Ban.time.desc())[:5]
		for ban in recent:
			p.message(info('Nick: %s' % ban.nick))

@policyHandler('connect_kick')
def allowClient(cn, pwd):
	p = player(cn)
	ip = p.ipLong()
	return not isIpBanned(ip) and not isNickBanned(p.name())

@eventHandler('player_kick')
@masterRequired
def onKick(cn, tcn):
	ban(tcn, 14500, config['Main']['default_reason'], cn)
	
@eventHandler('server_kick')
def onKick(cn):
	ban(cn, 14500, config['Main']['default_reason'], -1)

@commandHandler('kick')
@masterRequired
def onKickCommand(p, args):
	'''@description Kick player from the server without ban time
	   @usage <cn>'''
	tcn = int(args)
	t = player(tcn)
	serverMessage(info(config['Main']['kick_message'].substitute(colordict, name=t.name())))
	t.kick()

@commandHandler('insertban')
@masterRequired
def onInsertBan(p, args):
	'''@description Intert ban for ip address
	   @usage <ip> <seconds> (reason)'''
	args = args.split(' ')
	if len(args) < 2:
		raise UsageError('ip length (reason)')
	else:
		ip = ipStringToLong(args[0])
		length = int(args[1])
		try:
			reason = args[2]
		except IndexError:
		 	reason = 'Unspecified reason'
		expiration = time.time() + length
		newban = Ban(ip, expiration, reason, 'Unnamed', 0, 'Unnamed', time.time())
		session.add(newban)
		session.commit()
		p.message(info('Inserted ban for %s for %i seconds for %s.' % (ipLongToString(ip), length, reason)))

@commandHandler('banname')
@masterRequired
def onBanName(p, args):
	'''@description Ban name from the server
	   @usage <name>'''
	reason = args.split(' ')
	if len(reason) == 1:
		nick = reason[0]
		reason = 'Unspecified reason'
	else:
		nick = reason.pop(0)
		reason = args[len(nick)+1:]
	b = BanNick(nick, reason)
	session.add(b)
	session.commit()
	p.message(info('Inserted nick ban of %s for %s' % (nick, reason)))

def clearBans():
	bans = session.query(Ban).filter('expiration>'+str(time.time())).all()
	for b in bans:
		session.delete(b)
	session.commit()

@eventHandler('server_clear_bans')
@masterRequired
def reqClearBans(cn):
	clearBans()
	serverMessage(info('Bans cleared'))

@commandHandler('clearbans')
@masterRequired
def onClearBansCmd(p, args):
	'''@description Remove active bans
	   @usage'''
	clearBans()
	serverMessage(info('Bans cleared'))

gbans = {}

@policyHandler('connect_kick')
def isNotGBanned(cn, pwd):
	p = player(cn)
	try:
		gbans[p.ipString()]
		return False
	except KeyError:
		return True

@eventHandler('master_addgban')
def adGBan(ip_string):
	gbans[ip_string] = True

@eventHandler('master_cleargbans')
def clearGBans():
	gbans.clear()

