from DB.db import dbmanager
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
import sbserver
from xsbs.events import triggerServerEvent, registerServerEventHandler, registerPolicyEventHandler
from xsbs.commands import registerCommandHandler
from xsbs.colors import red, green, orange
from xsbs.ui import info, error
from xsbs.players import player
from xsbs.settings import PluginConfig

config = PluginConfig('usermanager')
usertable = config.getOption('Config', 'users_tablename', 'usermanager_users')
nicktable = config.getOption('Config', 'linkednames_table', 'usermanager_nickaccounts')
del config

Base = declarative_base()

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
	triggerServerEvent('player_logged_in', cn)
	sbserver.message(info(green(sbserver.playerName(cn)) + ' is verified'))

def userAuth(email, password):
	try:
		session= dbmanager.session()
		user = session.query(User).filter(User.email==email).filter(User.password==password).one()
		session.close()
	except NoResultFound:
		return False
	return user

def onRegisterCommand(cn, args):
	args = args.split(' ')
	if len(args) != 2:
		sbserver.playerMessage(cn, info('Usage: #register <email> <password>'))
	else:
		session = dbmanager.session()
		try:
			session.query(User).filter(User.email==args[0]).one()
		except NoResultFound:
			user = User(args[0], args[1])
			session.add(user)
			session.commit()
			sbserver.playerMessage(cn, green('Account created'))
		else:
			sbserver.playerMessage(cn, error('An account with that email address already exists.'))
		session.close()

def onLoginCommand(cn, args):
	args = args.split(' ')
	if len(args) != 2:
		sbserver.playerMessage(cn, info('Usage: #login <email> <password>'))
		return
	user = userAuth(args[0], args[1])
	if user:
		login(cn, user)
	else:
		sbserver.playerMessage(cn, error('Invalid login.'))

def onLinkName(cn, args):
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #linkname'))
		return
	if not isLoggedIn(cn):
		sbserver.playerMessage(cn, error('You must be logged in to link a name to your account.'))
		return
	try:
		session = dbmanager.session()
		session.query(NickAccount).filter(NickAccount.nick==sbserver.playerName(cn)).one()
		session.close()
	except NoResultFound:
		pass
	else:
		sbserver.playerMessage(cn, error('Your name is already linked to an account.'))
		return
	user = loggedInAs(cn)
	nickacct = NickAccount(sbserver.playerName(cn), user.id)
	session = dbmanager.session()
	session.add(nickacct)
	session.commit()
	session.close()
	sbserver.playerMessage(cn, info('Your name is now linked to your account.'))

def onSetMaster(cn, givenhash):
	nick = sbserver.playerName(cn)
	session = dbmanager.session()
	try:
		na = session.query(NickAccount).filter(NickAccount.nick==nick).one()
	except NoResultFound:
		if sbserver.playerPrivilege(cn) <= 1:
			sbserver.playerMessage(cn, error('Your name is not assigned to any accounts.'))
	else:
		nickhash = sbserver.hashPassword(cn, na.user.password)
		if givenhash == nickhash:
			login(cn, na.user)
		else:
			sbserver.playerMessage(cn, error('Invalid password'))
	session.close()

Base.metadata.create_all(dbmanager.engine)

registerCommandHandler('register', onRegisterCommand)
registerCommandHandler('login', onLoginCommand)
registerCommandHandler('linkname', onLinkName)
registerServerEventHandler('player_setmaster', onSetMaster)

