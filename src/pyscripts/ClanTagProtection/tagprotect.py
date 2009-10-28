from xsbs.events import registerServerEventHandler, execLater
from xsbs.players import player
from xsbs.ui import warning
from xsbs.colors import red
from UserManager.usermanager import User
from NickReserve.nickreserve import nickReserver
import sbserver
from DB.db import dbmanager
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
	tag = Column(String)
	def __init__(self, tag):
		self.tag = tag

class ClanMember(Base):
	__tablename__ = 'clanmember'
	id = Column(Integer, primary_key=True)
	tag_id = Column(Integer)
	user_id = Column(Integer)
	tag = relation(ClanTag, primaryjoin=tag_id=ClanTag.id)
	user = relation(User, primaryjoin=user_id=User.id)
	def __init__(self, tag_id, user_id):
		self.tag_id = tag_id
		self.user_id = user_id

def warnTagReserved(cn, count, sessid):
	try:
		p = player(cn)
	except ValueError:
		return
	if len(p.registered_tags) == 0:
		return
	if count > 4:
		ban(cn, 0, 'Use of reserved clan tag', -1)
		p.warning_for_login = False
		return
	remaining = 25-(count*5)
	sbserver.playerMessage(cn, warning('Your are using a reserved clan tag. You have ' + red('%i') + ' seconds to login or be kicked.') % remaining)
	addTimer(5000, warnNickReserved, (cn, count+1, sessid))

def setUsedTags(cn):
	nick = sbserver.playerName(cn)
	p = player(cn)
	potentials = []
	matches = regex.findall(nick)
	for match in matches:
		potentials.append(match)
	for potential in potentials:
		if isTag(potential):
			try:
				p.registered_tags.append(potential)
			except AttibuteError:
				p.registered_tags = [potential]

def onLogin(cn):
	try:
		p = player(cn)
		u = player.user
	except AttributeError:
		logging.error('Got login event but no user object for player.')
	try:
		for tag in p.registered_tags:
			if userBelongsTo(tag):
				p.registered_tags.pop(0)
			else:
				ban(cn, 0, 'Use of reserved clan tag', -1)
	except AttributeError:
		return

def initCheck(cn):
	p = player(cn)
	try:
		if p.warning_for_login:
			return
	except AttributeError:
		pass
	warnTagReserved(cn, 0, sbserver.playerSessionId(cn))

def onConnect(cn):
	setUsedTags(sbserver.playerName(cn))
	sbserver.execLater(initCheck, (cn,))
	try:
		if len(p.registered_tags) > 0:
			registerServerEventHandler('player_logged_in', onLogin)
	except AttributeError:
		pass

def onNameChange(cn, name):
	onConnect(cn)

registerServerEventHandler('player_connect_delayed', onConnect)
registerServerEventHandler('player_name_changed', onNameChange)

