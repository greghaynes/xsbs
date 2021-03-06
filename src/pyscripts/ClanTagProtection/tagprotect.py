from xsbs.events import eventHandler, execLater, registerServerEventHandler
from xsbs.players import player
from xsbs.ui import warning
from xsbs.colors import red
from xsbs.timers import addTimer
from xsbs.db import dbmanager
from xsbs.ban import ban
from xsbs.users import User, isLoggedIn

from sqlalchemy.orm import relation
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

import re
import logging

regex = '\[.{1,5}\]|<.{1,5}>|\{.{1,5}\}|\}.{1,5}\{|.{1,5}\||\|.{1,5}\|'
regex = re.compile(regex)

Base = declarative_base()
session = dbmanager.session()

class ClanTag(Base):
	__tablename__ = 'clantags'
	id = Column(Integer, primary_key=True)
	tag = Column(String, index=True)
	def __init__(self, tag):
		self.tag = tag

class ClanMember(Base):
	__tablename__ = 'clanmember'
	id = Column(Integer, primary_key=True)
	tag_id = Column(Integer, index=True)
	user_id = Column(Integer, index=True)
	def __init__(self, tag_id, user_id):
		self.tag_id = tag_id
		self.user_id = user_id

def warnTagReserved(cn, count, sessid, nick):
	try:
		p = player(cn)
	except ValueError:
		return
	if p.name() != nick or sessid != p.sessionId():
		return
	if len(p.registered_tags) == 0:
		return
	if count > 4:
		ban(cn, 0, 'Use of reserved clan tag', -1)
		p.warning_for_login = False
		return
	remaining = 25-(count*5)
	p.message(warning('Your are using a reserved clan tag. You have ' + red('%i') + ' seconds to login or be kicked.') % remaining)
	addTimer(5000, warnTagReserved, (cn, count+1, sessid, nick))

def tagId(tag):
	return dbmanager.query(ClanTag).filter(ClanTag.tag==tag).one().id

def setUsedTags(cn):
	try:
		p = player(cn)
	except ValueError:
		return
	nick = p.name()
	potentials = []
	matches = regex.findall(nick)
	for match in matches:
		potentials.append(match)
	p.registered_tags = []
	for potential in potentials:
			try:
				id = tagId(potential)
				p.registered_tags.append(id)
			except NoResultFound:
				pass

def userBelongsTo(user, tag_id):
	try:
		dbmanager.query(ClanMember).filter(ClanMember.tag_id==tag_id).filter(ClanMember.user_id==user.id).one()
		return True
	except NoResultFound:
		return False

def onLogin(cn):
	try:
		p = player(cn)
		u = p.user
	except AttributeError:
		logging.error('Got login event but no user object for player.')
		return
	try:
		for tag in p.registered_tags:
			t = p.registered_tags.pop(0)
			if userBelongsTo(u, t):
				return
			else:
				ban(cn, 0, 'Use of reserved clan tag', -1)
	except AttributeError:
		return

def initCheck(cn):
	if isLoggedIn(cn):
		onLogin(cn)
		return
	p = player(cn)
	try:
		if p.warning_for_login:
			return
	except AttributeError:
		pass
	else:
		warnTagReserved(cn, 0, p.sessionId(), p.name())

@eventHandler('player_connect_delayed')
def onConnect(cn):
	setUsedTags(cn)
	p = player(cn)
	try:
		if len(p.registered_tags) > 0:
			execLater(initCheck, (cn,))
			registerServerEventHandler('player_logged_in', onLogin)
	except AttributeError:
		pass

@eventHandler('player_name_changed')
def onNameChange(cn, oldname, newname):
	onConnect(cn)

Base.metadata.create_all(dbmanager.engine)

