import sbserver
from xsbs.settings import PluginConfig
from xsbs.colors import red, colordict
from xsbs.ui import insufficientPermissions, error, info
from xsbs.events import triggerServerEvent, registerServerEventHandler, registerPolicyEventHandler, execLater
from UserPrivelege.userpriv import registerCommandHandler, masterRequired
from xsbs.net import ipLongToString, ipStringToLong
from DB.db import dbmanager
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
	ip = Column(Integer)
	expiration = Column(Integer) # Epoch seconds
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


def getCurrentBanByIp(ipaddress):
	return session.query(Ban).filter(Ban.ip==ipaddress).filter('expiration>'+str(time.time())).one()

def isCurrentlyBanned(ipaddress):
	try:
		b = getCurrentBanByIp(ipaddress)
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

def onRecentBans(cn, args):
	if sbserver.playerPrivilege(cn) == 0:
		insufficientPermissions(cn)
	elif args != '':
		sbserver.playerMessage(cn, error('Usage: #recentbans'))
	else:
		recent = session.query(Ban).order_by(Ban.time.desc())[:5]
		for ban in recent:
			sbserver.playerMessage(cn, info('Nick: %s' % ban.nick))

def allowClient(cn, pwd):
	ip = sbserver.playerIpLong(cn)
	return not isCurrentlyBanned(ip)

@masterRequired
def onKick(cn, tcn):
	ban(tcn, 14500, 'Unspecified reason', cn)

@masterRequired
def onKickCommand(cn, args):
	tcn = int(args)
	sbserver.message(info(kick_message.substitute(colordict, name=sbserver.playerName(tcn))))
	sbserver.playerKick(tcn)

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
def init():
	registerPolicyEventHandler("connect_kick", allowClient)
	registerCommandHandler('ban', onBanCmd)
	registerCommandHandler('recentbans', onRecentBans)
	registerCommandHandler('kick', onKickCommand)
	registerCommandHandler('insertban', onInsertBan)
	registerServerEventHandler('player_ban', ban)
	registerServerEventHandler('player_kick', onKick)
	Base.metadata.create_all(dbmanager.engine)

init()
