from DB.db import dbmanager
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.ext.declarative import declarative_base
import sbserver, sbevents, sbtools

Base = declarative_base()
session = dbmanager.session()
verified_users = {}

class User(Base):
	__tablename__ = 'usermanager_users'
	id = Column(Integer, primary_key=True)
	email = Column(String)
	password = Column(String)
	def __init__(self, email, password):
		self.email = email
		self.password = password

class NickAccount(Base):
	__tablename__ = 'usermanager_nickaccounts'
	id = Column(Integer, primary_key=True)
	nick = Column(String)
	user_id = Column(Integer, ForeignKey('usermanager_users.id'))
	user = relation(User, primaryjoin=user_id==User.id)
	def __init__(self, nick, user_id):
		self.nick = nick
		self.user_id = user_id

def loggedInAs(cn):
	return verified_users[cn]

def isLoggedIn(cn):
	return verified_users.has_key(cn)

def login(cn, user):
	if not verified_users.has_key(cn):
		sbserver.message(sbtools.green(sbserver.playerName(cn)) + ' is ' + sbtools.orange('verified') + '.')
		verified_users[cn] = user

def userAuth(email, password):
	user = session.query(User).filter(User.email==email).filter(User.password==password).one()
	return user

def onRegisterCommand(cn, args):
	args = args.split(' ')
	if len(args) != 2:
		sbserver.playerMessage(cn, sbtools.red('Usage: #register <email> <password>'))
		return
	elif session.query(User).filter(User.email==args[0]).one():
		sbserver.playerMessage(cn, sbtools.red('An account with that email address already exists.'))
	else:
		user = User(args[0], args[1])
		session.add(user)

def onLoginCommand(cn, args):
	args = args.split(' ')
	if len(args) != 2:
		sbserver.playerMessage(cn, sbtools.red('Usage: #login <email> <password>'))
		return
	user = userAuth(args[0], args[1])
	if user:
		login(cn, user)
	else:
		sbserver.playerMessage(cn, sbtools.red('Invalid login.'))

def onLinkName(cn, args):
	if args != '':
		sbserver.playerMessage(cn, sbtools.red('Usage: #linkname'))
		return
	if not isLoggedIn(cn):
		sbserver.playerMessage(cn, sbtools.red('You must be logged in to link a name to your account.'))
		return
	user = loggedInAs(cn)
	nickacct = NickAccount(sbserver.playerName(cn), user.id)
	session.add(nickacct)
	sbserver.playerMessage(cn, sbtools.green('Your name is now linked to your account.'))

def onSetMaster(cn, givenhash):
	nick = sbserver.playerName(cn)
	na = session.query(NickAccount).filter(NickAccount.nick==nick).one()
	if not na:
		sbserver.playerMessage(cn, sbtools.red('Your name is not assigned to any accounts.'))
		return
	nickhash = sbserver.hashPassword(cn, na.user.password)
	if givenhash == nickhash:
		login(cn, na.user)
	else:
		sbserver.playerMessage(cn, sbtools.red('Invalid password'))

def onDisconnect(cn):
	try:
		del verified_users[cn]
	except KeyError:
		pass

def onShutdown():
	session.commit()

Base.metadata.create_all(dbmanager.engine)

sbevents.registerCommandHandler('register', onRegisterCommand)
sbevents.registerCommandHandler('login', onLoginCommand)
sbevents.registerCommandHandler('linkname', onLinkName)
sbevents.registerEventHandler('server_stop', onShutdown)
sbevents.registerEventHandler('player_disconnect', onDisconnect)
sbevents.registerPolicyEventHandler('player_setmaster', onSetMaster)
