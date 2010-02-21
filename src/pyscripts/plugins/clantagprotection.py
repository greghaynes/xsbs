from xsbs.events import eventHandler, execLater, registerServerEventHandler
from xsbs.players import player
from xsbs.ui import warning
from xsbs.colors import red
from xsbs.timers import addTimer
from xsbs.ban import ban
from xsbs.users import User, Group, isLoggedIn

from elixir import Entity, Field, String, Integer, ManyToOne, OneToMany, setup_all, session
from sqlalchemy.orm.exc import NoResultFound

import re
import logging

regex = '\[.{1,5}\]|<.{1,5}>|\{.{1,5}\}|\}.{1,5}\{|.{1,5}\||\|.{1,5}\|'
regex = re.compile(regex)

class ClanTag(Entity):
	tag = Field(String, index=True)
	group = ManyToOne(Group)
	def __init__(self, tag):
		self.tag = tag

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
	return session.query(ClanTag).filter(ClanTag.tag==tag).one().id

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

def userBelongsTo(user, tag):
	return False
	try:
		## TODO
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

