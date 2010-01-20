from xsbs.db import dbmanager
from xsbs.settings import PluginConfig
from xsbs.net import ipLongToString, ipStringToLong
from xsbs.timers import addTimer
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from xsbs.ui import info, notice
from xsbs.colors import colordict
import time, string
import logging
import sbserver

config = PluginConfig('bans')
ban_message = config.getOption('Config', 'message', 'Banning ${orange}${name}${white} for $seconds seconds for ${red}${reason}')
del config
ban_message = string.Template(ban_message)

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
	except MultipleResultsFound:
		return True

def isNickBanned(nick):
	try:
		b = getCurrentBanByNick(nick)
		return True
	except NoResultFound:
		return False
	except MultipleResultsFound:
		return True

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
	addTimer(200, sbserver.playerKick, (cn,))
	logging.info('Player %s (%s) banned for %s by %s (%s)',
		nick,
		ipLongToString(ip),
		reason,
		banner_nick,
		ipLongToString(banner_ip))
	sbserver.message(info(ban_message.substitute(colordict, name=nick, seconds=seconds, reason=reason)))

Base.metadata.create_all(dbmanager.engine)

