import sbserver
from xsbs.settings import PluginConfig
from xsbs.colors import red, colordict
from xsbs.ui import insufficientPermissions, error, info
from xsbs.db import dbmanager
from xsbs.commands import commandHandler
from xsbs.events import triggerServerEvent, registerServerEventHandler, registerPolicyEventHandler, execLater
from UserPrivilege.userpriv import masterRequired
from xsbs.net import ipLongToString, ipStringToLong
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
import time, string
import logging

config = PluginConfig('bans')
ban_command = config.getOption('Config', 'ban_command', 'ban')
default_ban_length = config.getOption('Config', 'default_ban_time', 3600)
ban_message = config.getOption('Config', 'message', 'Banning ${orange}${name}${white} for $seconds seconds for ${red}${reason}')
default_reason = config.getOption('Config', 'default_reason', 'unspecified reason')
kick_message = config.getOption('Config', 'kick_message', '${green}${name}${white} was ${red}kicked${white} from server')
del config
ban_message = string.Template(ban_message)
kick_message = string.Template(kick_message)

Base = declarative_base()
session = dbmanager.session()

class Ban(Base):
	__tablename__='bans'
	id = Column(Integer, primary_key=True)
	ip = Column(Integer, index=True)
	expiration = Column(Integer, index=True) # Epoch seconds
	reason = Column(String)
	nick = Column(String)
	banner_ip = Column(Integer)
	banner_nick = Column(String)
	time = Column(Integer)
	def __init__(self, ip, expiration, reason, nick, banner_ip, banner_nick, time):
		self.ip = ip
		self.expiration = expiration
		self.reason = reason
		self.nick = nick
		self.banner_ip = banner_ip
		self.banner_nick = banner_nick
		self.time = time
	def isExpired(self):
		return self.expiration <= time.time()

class BanNick(Base):
	__tablename__='banned_nicks'
	id = Column(Integer, primary_key=True)
	nick = Column(String, index=True)
	reason = Column(String)
	def __init__(self, nick, reason):
		self.nick = nick
		self.reason = reason

def getCurrentBanByIp(ipaddress):
	return session.query(Ban).filter(Ban.ip==ipaddress).filter('expiration>'+str(time.time())).one()

def getCurrentBanByNick(nick):
	return session.query(BanNick).filter(BanNick.nick==nick).one()

def isIpBanned(ipaddress):
	try:
		b = getCurrentBanByIp(ipaddress)
		return True
	except NoResultFound:
		return False

def isNickBanned(nick):
	try:
		b = getCurrentBanByNick(nick)
		return True
	except NoResultFound:
		return False

def ban(cn, seconds, reason, banner_cn):
	ip = sbserver.playerIpLong(cn)
	expiration = time.time() + seconds
	nick = sbserver.playerName(cn)
	if banner_cn != -1:
		banner_ip = sbserver.playerIpLong(banner_cn)
		banner_nick = sbserver.playerName(banner_cn)
	else:
		banner_ip = 0
		banner_nick = ''
	newban = Ban(ip, expiration, reason, nick, banner_ip, banner_nick, time.time())
	session.add(newban)
	session.commit()
	execLater(sbserver.playerKick, (cn,))
	logging.info('Player %s (%s) banned for %s by %s (%s)',
		nick,
		ipLongToString(ip),
		reason,
		banner_nick,
		ipLongToString(banner_ip))
	sbserver.message(info(ban_message.substitute(colordict, name=nick, seconds=seconds, reason=reason)))

@masterRequired
def onBanCmd(cn, text):
	'''@description Ban user from server
	   @usage <seconds> (reason)'''
	sp = text.split(' ')
	try:
		tcn = int(sp[0])
		try:
			ip = sbserver.playerIpLong(tcn)
		except ValueEror:
			sbserver.playerMessage(cn, error('Invalid cn'))
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
		ban(tcn, length, reason, cn)
	except (ValueError, KeyError):
		sbserver.playerMessage(cn, error('Usage: #ban <cn> (duration) (reason)'))

@commandHandler('recentbans')
@masterRequired
def onRecentBans(cn, args):
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #recentbans'))
	else:
		recent = session.query(Ban).order_by(Ban.time.desc())[:5]
		for ban in recent:
			sbserver.playerMessage(cn, info('Nick: %s' % ban.nick))

def allowClient(cn, pwd):
	ip = sbserver.playerIpLong(cn)
	return not isIpBanned(ip) and not isNickBanned(sbserver.playerName(cn))

@masterRequired
def onKick(cn, tcn):
	ban(tcn, 14500, 'Unspecified reason', cn)

@commandHandler('kick')
@masterRequired
def onKickCommand(cn, args):
	tcn = int(args)
	sbserver.message(info(kick_message.substitute(colordict, name=sbserver.playerName(tcn))))
	sbserver.playerKick(tcn)

@commandHandler('insertban')
@masterRequired
def onInsertBan(cn, args):
	args = args.split(' ')
	if len(args) < 2:
		sbserver.playerMessage(cn, error('Usage: #insertban <ip> <length> (reason)'))
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
		sbserver.playerMessage(cn, info('Inserted ban for %s for %i seconds for %s.' % (ipLongToString(ip), length, reason)))

@commandHandler('banname')
@masterRequired
def onBanName(cn, args):
	'''@description Ban name from the server'''
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
	sbserver.playerMessage(cn, info('Inserted nick ban of %s for %s' % (nick, reason)))

def clearBans():
	bans = session.query(Ban).filter('expiration>'+str(time.time())).all()
	for b in bans:
		session.delete(b)
	session.commit()

@masterRequired
def reqClearBans(cn):
	clearBans()
	sbserver.message(info('Bans cleared'))

@commandHandler('clearbans')
@masterRequired
def onClearBansCmd(cn, args):
	clearBans()
	sbserver.message(info('Bans cleared'))

def init():
	registerPolicyEventHandler("connect_kick", allowClient)
	registerServerEventHandler('player_ban', ban)
	registerServerEventHandler('player_kick', onKick)
	registerServerEventHandler('server_clear_bans', reqClearBans)
	Base.metadata.create_all(dbmanager.engine)

init()
