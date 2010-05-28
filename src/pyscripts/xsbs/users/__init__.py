from elixir import Entity, Field, String, ManyToOne, OneToMany, setup_all, session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from xsbs.events import eventHandler, triggerServerEvent, registerServerEventHandler, registerPolicyEventHandler
from xsbs.commands import commandHandler, UsageError, StateError, ArgumentValueError
from xsbs.colors import red, green, orange
from xsbs.ui import info, error, warning
from xsbs.players import player, currentAdmin, currentMaster
from xsbs.settings import loadPluginConfig
from xsbs.ban import ban
from xsbs.timers import addTimer

import sbserver
import re

config = {
	'Main': {
		'blocked_reserved_names': 'unnamed, admin',
		}
	}

config['Main']['blocked_reserved_names'] = config['Main']['blocked_reserved_names'].strip(' ').split(',')

class NickAccount(Entity):
	nick = Field(String(15))
	user = ManyToOne('User')
	def __init__(self, nick, user):
		self.nick = nick
		self.user = user

class Group(Entity):
	name = Field(String(30))
	users = OneToMany('User')
	def __init__(self, name):
		self.name = name

class User(Entity):
	email = Field(String(50))
	password = Field(String(20))
	nickaccounts = OneToMany('NickAccount')
	groups = ManyToOne('Group')
	def __init__(self, email, password):
		self.email = email
		self.password = password

def loggedInAs(cn):
	return player(cn).user

def isLoggedIn(cn):
	try:
		return player(cn).logged_in
	except (AttributeError, ValueError):
		return False

def login(cn, user):
	if isLoggedIn(cn):
		raise StateError('You are already logged in')
	player(cn).user = user
	player(cn).logged_in = True
	triggerServerEvent('player_logged_in', (cn,))
	sbserver.message(info(green(sbserver.playerName(cn)) + ' is verified'))

def userAuth(email, password):
	try:
		user = User.query.filter(User.email==email).filter(User.password==password).one()
	except (NoResultFound, MultipleResultsFound):
		return False
	return user

def isValidEmail(email):
	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			return True
	return False

@commandHandler('register')
def onRegisterCommand(p, args):
	'''@description Register account with server
	   @usage email password
	   @public'''
	args = args.split(' ')
	if len(args) != 2:
		raise UsageError()
	try:
		User.query.filter(User.email==args[0]).one()
	except NoResultFound:
		if not isValidEmail(args[0]):
			raise ArgumentValueError('Invalid email address')
		user = User(args[0], args[1])
		session.commit()
		p.message(info('Account created'))
		return
	except MultipleResultsFound:
		pass
	raise StateError('An account with that email already exists')

@commandHandler('login')
def onLoginCommand(p, args):
	'''@description Login to server account
	   @usage email password
	   @public'''
	args = args.split(' ')
	if len(args) != 2:
		raise UsageError()
	user = userAuth(args[0], args[1])
	if user:
		login(p.cn, user)
	else:
		p.message(error('Invalid login.'))

@commandHandler('linkname')
def onLinkName(p, args):
	'''@description Link name to server account, and reserve name.
	   @usage
	   @public'''
	if args != '':
		raise UsageError()
	if not isLoggedIn(p.cn):
		raise StateError('You must be logged in to link a name to your account')
	if p.name() in config['Main']['blocked_reserved_names']:
		raise StateError('You cannot reserve this name')
	try:
		NickAccount.query.filter(NickAccount.nick==p.name()).one()
	except NoResultFound:
		user = loggedInAs(p.cn)
		nickacct = NickAccount(p.name(), user)
		session.commit()
		p.message(info('\"%s\" is now linked to your account.' % p.name()))
		p.message(info('You may now login with /setmaster password'))
		return
	except MultipleResultsFound:
		pass
	raise StateError('Your name is already linked to an account')

@commandHandler('newuser')
def onNewuserCommand(p, args):
	'''@description Register account with server
	   @usage email password
	   @public'''
	onRegisterCommand(p.cn, args)
	onLoginCommand(p.cn, args)
	onLinkName(p.cn, '')

@commandHandler('changepass')
def onChangepass(p, args):
	'''@description Change your password
	   @usage old_password new_password
	   @public'''
	args = args.split(' ')
	if len(args) != 2:
		raise UsageError()
	if not isLoggedIn(p.cn):
		raise StateError('You must be logged in to change your password')
	try:
		User.query.filter(User.id==loggedInAs(p.cn).id).filter(User.password==args[0]).one()
	except NoResultFound:
		raise StateError('Incorrect password.')
	except MultipleResultsFound:
		pass
	else:
		if not isValidPassword(args[1], p.cn):
			raise ArgumentValueError('Invalid password')
		User.query.filter(User.id==loggedInAs(p.cn).id).update({ 'password': args[1] })
		session.commit()
		return

@eventHandler('player_setmaster')
def onSetMaster(cn, givenhash):
	p = player(cn)
	adminhash = sbserver.hashPassword(cn, sbserver.adminPassword())
	try:
		na = NickAccount.query.filter(NickAccount.nick==p.name()).one()
	except NoResultFound:
		if givenhash != adminhash:
			setSimpleMaster(cn)
	except MultipleResultsFound:
		p.message(error(' This name is linked to multiple accounts.  Contact the system administrator.'))
	else:
		nickhash = sbserver.hashPassword(cn, na.user.password)
		if givenhash == nickhash:
			login(cn, na.user)
		else:
			if givenhash != adminhash:
				setSimpleMaster(cn)

def setSimpleMaster(cn):
	p = player(cn)
	if sbserver.publicServer() == 1:
		sbserver.playerMessage(cn, error('This is not an open server, you need auth or master privileges to get master.'))
		return
	if currentAdmin() != None:
		sbserver.playerMessage(cn, error('Admin is present'))
		return
	if currentMaster() != None:
		sbserver.playerMessage(cn, error('Master is present'))
		return
	sbserver.setMaster(cn)

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
	return NickAccount.query.filter(NickAccount.nick==nick).one()

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

