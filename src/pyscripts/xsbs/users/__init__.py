from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
import sbserver
from xsbs.db import dbmanager
from xsbs.events import eventHandler, triggerServerEvent, registerServerEventHandler, registerPolicyEventHandler
from xsbs.commands import commandHandler
from xsbs.colors import red, green, orange
from xsbs.ui import info, error, warning
from xsbs.players import player
from xsbs.settings import PluginConfig
from xsbs.ban import ban
from xsbs.timers import addTimer
import re

config = PluginConfig('usermanager')
usertable = config.getOption('Config', 'users_tablename', 'usermanager_users')
nicktable = config.getOption('Config', 'linkednames_table', 'usermanager_nickaccounts')
blocked_names = config.getOption('Config', 'blocked_names', 'unnamed, admin')
del config

blocked_names = blocked_names.strip(' ').split(',')

Base = declarative_base()
session = dbmanager.session()

class User(Base):
	__tablename__ = usertable
	id = Column(Integer, primary_key=True)
	email = Column(String, index=True)
	password = Column(String, index=True)
	def __init__(self, email, password):
		self.email = email
		self.password = password

class NickAccount(Base):
	__tablename__ = nicktable
	id = Column(Integer, primary_key=True)
	nick = Column(String, index=True)
	user_id = Column(Integer, ForeignKey('usermanager_users.id'))
	user = relation(User, primaryjoin=user_id==User.id)
	def __init__(self, nick, user_id):
		self.nick = nick
		self.user_id = user_id

def loggedInAs(cn):
	return player(cn).user

def isLoggedIn(cn):
	try:
		return player(cn).logged_in
	except (AttributeError, ValueError):
		return False

def login(cn, user):
	if isLoggedIn(cn):
		sbserver.playerMessage(cn, error('You are already logged in'))
		return
	player(cn).user = user
	player(cn).logged_in = True
	triggerServerEvent('player_logged_in', (cn,))
	sbserver.message(info(green(sbserver.playerName(cn)) + ' is verified'))

def userAuth(email, password):
	try:
		user = session.query(User).filter(User.email==email).filter(User.password==password).one()
	except (NoResultFound, MultipleResultsFound):
		return False
	return user

def isValidEmail(email):
	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			return 1
	return 0

@commandHandler('register')
def onRegisterCommand(cn, args):
	'''@description Register account with server
	   @usage <email> <password>
	   @public'''
	args = args.split(' ')
	if len(args) != 2:
		sbserver.playerMessage(cn, info('Usage: #register <email> <password>'))
		return
	try:
		session.query(User).filter(User.email==args[0]).one()
	except NoResultFound:
		user = User(args[0], args[1])
		session.add(user)
		session.commit()
		sbserver.playerMessage(cn, green('Account created'))
		return
	except MultipleResultsFound:
		pass
	sbserver.playerMessage(cn, error('An account with that email address already exists.'))

@commandHandler('login')
def onLoginCommand(cn, args):
	'''@description Login to server account
	   @usage <email> <password>
	   @public'''
	args = args.split(' ')
	if len(args) != 2:
		sbserver.playerMessage(cn, info('Usage: #login <email> <password>'))
		return
	user = userAuth(args[0], args[1])
	if user:
		login(cn, user)
	else:
		sbserver.playerMessage(cn, error('Invalid login.'))

@commandHandler('linkname')
def onLinkName(cn, args):
	'''@description Link name to server account, and reserve name.
	   @usage
	   @public'''
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #linkname'))
		return
	if not isLoggedIn(cn):
		sbserver.playerMessage(cn, error('You must be logged in to link a name to your account.'))
		return
	if sbserver.playerName(cn) in blocked_names:
		sbserver.playerMessage(cn, error('You cannot reserve your current name.'))
		return
	try:
		session.query(NickAccount).filter(NickAccount.nick==sbserver.playerName(cn)).one()
	except NoResultFound:
		user = loggedInAs(cn)
		nickacct = NickAccount(sbserver.playerName(cn), user.id)
		session.add(nickacct)
		session.commit()
		sbserver.playerMessage(cn, info('Your name is now linked to your account.'))
		return
	except MultipleResultsFound:
		pass
	sbserver.playerMessage(cn, error('Your name is already linked to an account.'))

@commandHandler('newuser')
def onNewuserCommand(cn, args):
	'''@description Register account with server
	   @usage <email> <password>
	   @public'''
	args = args.split(' ')
	if len(args) != 2:
		sbserver.playerMessage(cn, info('Usage: #newuser <email> <password>'))
		return
	if sbserver.playerName(cn) in blocked_names:
		sbserver.playerMessage(cn, error('You cannot reserve your current name.'))
		return
	try:
		session.query(User).filter(User.email==args[0]).one()
	except NoResultFound:
		user = User(args[0], args[1])
		session.add(user)
		session.commit()
		sbserver.playerMessage(cn, green('Account created'))
	except MultipleResultsFound:
		return
	else:
		sbserver.playerMessage(cn, error('An account with that email address already exists.'))
	userlogin = userAuth(args[0], args[1])
	if userlogin:
		login(cn, userlogin)
		sbserver.playerMessage(cn, green('You are logged in.'))
	else:
		sbserver.playerMessage(cn, error('Invalid login. This means something REALLY got fucked, tell an admin.'))
		return
	try:
		session.query(NickAccount).filter(NickAccount.nick==sbserver.playerName(cn)).one()
	except NoResultFound:
		user = loggedInAs(cn)
		nickacct = NickAccount(sbserver.playerName(cn), user.id)
		session.add(nickacct)
		session.commit()
		sbserver.playerMessage(cn, green('Your name is now linked to your account.'))
		sbserver.playerMessage(cn, red('You may now login with /setmaster %s' % args[1]))
		return
	except MultipleResultsFound:
		pass
	else:
		sbserver.playerMessage(cn, error('Your name is already linked to an account.'))

@eventHandler('player_setmaster')
def onSetMaster(cn, givenhash):
	nick = sbserver.playerName(cn)
	adminhash = sbserver.hashPassword(cn, sbserver.adminPassword())
	try:
		na = session.query(NickAccount).filter(NickAccount.nick==nick).one()
	except NoResultFound:
		if givenhash != adminhash:
			sbserver.playerMessage(cn, error('Your name is not assigned to any accounts.'))
	except MultipleResultsFound:
		sbserver.playerMessage(cn, error('Multiple names linked to account. Contact system administrator.'))
	else:
		nickhash = sbserver.hashPassword(cn, na.user.password)
		if givenhash == nickhash:
			login(cn, na.user)
		else:
			if givenhash != adminhash:
				sbserver.playerMessage(cn, error('Invalid password'))

def warnNickReserved(cn, count, sessid):
	try:
		p = player(cn)
	except ValueError:
		return
	try:
		nickacct = p.warn_nickacct
		if nickacct.nick != sbserver.playerName(cn) or sessid != sbserver.playerSessionId(cn):
			p.warning_for_login = False
			return
	except (AttributeError, ValueError):
		p.warning_for_login = False
		return
	if isLoggedIn(cn):
		user = loggedInAs(cn)
		if nickacct.user_id != user.id:
			ban(cn, 0, 'Use of reserved name', -1)
		p.warning_for_login = False
		return
	if count > 4:
		ban(cn, 0, 'Use of reserved name', -1)
		p.warning_for_login = False
		return
	remaining = 25-(count*5)
	sbserver.playerMessage(cn, warning('Your name is reserved. You have ' + red('%i') + ' seconds to login or be kicked.') % remaining)
	addTimer(5000, warnNickReserved, (cn, count+1, sessid))

def nickReserver(nick):
	return session.query(NickAccount).filter(NickAccount.nick==nick).one()

@eventHandler('player_connect')
def onPlayerActive(cn):
	nick = sbserver.playerName(cn)
	p = player(cn)
	try:
		nickacct = nickReserver(sbserver.playerName(cn))
	except NoResultFound:
		p.warning_for_login = False
		return
	p = player(cn)
	p.warning_for_login = True
	p.warn_nickacct = nickacct
	warnNickReserved(cn, 0, sbserver.playerSessionId(cn))

@eventHandler('player_name_changed')
def onPlayerNameChanged(cn, old_name, new_name):
	onPlayerActive(cn)

Base.metadata.create_all(dbmanager.engine)

