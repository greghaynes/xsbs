from DB.db import dbmanager
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sbserver, sbevents, sbtools

Base = declarative_base()
session = dbmanager.session()
verified_users = []

class User(Base):
	__tablename__ = 'usermanager_users'
	id = Column(Integer, primary_key=True)
	email = Column(String)
	password = Column(String)
	def __init__(self, email, password):
		self.email = email
		self.password = password

def isLoggedIn(cn):
	return cn in verified_users

def login(cn):
	if cn not in verified_users:
		verified_users.append(cn)

def userAuth(email, password):
	users = session.query(User).filter(User.email==email).filter(User.password==password).all()
	return len(users) >= 1


def onRegisterCommand(cn, args):
	args = args.split(' ')
	if len(args) != 2:
		sbserver.playerMessage(cn, sbtools.red('Usage: #register <email> <password>'))
		return
	elif session.query(User).filter(User.email==args[0]) >= 1:
		sbserver.playerMessage(cn, sbtools.red('An account with that email address already exists.'))
	else:
		user = User(args[0], args[1])
		session.add(user)

def onLoginCommand(cn, args):
	args = args.split(' ')
	if len(args) != 2:
		sbserver.playerMessage(cn, sbtools.red('Usage: #login <email> <password>'))
		return
	if userAuth(args[0], args[1]):
		login(cn)
		sbserver.message(sbtools.green(sbserver.playerName(cn)) + ' is ' + sbtools.orange('verified') + '.')
	else:
		sbserver.playerMessage(cn, sbtools.red('Invalid login.'))

def onDisconnect(cn):
	try:
		verified_users.remove(cn)
	except ValueError:
		pass

def onShutdown():
	session.commit()

Base.metadata.create_all(dbmanager.engine)

sbevents.registerCommandHandler('register', onRegisterCommand)
sbevents.registerCommandHandler('login', onLoginCommand)
sbevents.registerEventHandler('server_stop', onShutdown)
sbevents.registerEventHandler('player_disconnect', onDisconnect)

