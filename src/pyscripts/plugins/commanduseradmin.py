from xsbs.commands import commandHandler, UsageError, StateError, ArgumentValueError
from xsbs.ui import info, error, warning
from xsbs.users import User, NickAccount, config as userConfig
from xsbs.events import eventHandler
from xsbs.players import player, currentAdmin, currentMaster
import sbserver

from elixir import session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

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
		p.login(user)
	else:
		p.message(error('Invalid login.'))

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

@commandHandler('linkname')
def onLinkName(p, args):
	'''@description Link name to server account, and reserve name.
	   @usage
	   @public'''
	if args != '':
		raise UsageError()
	if not p.isLoggedIn():
		raise StateError('You must be logged in to link a name to your account')
	if p.name() in userConfig['Main']['blocked_reserved_names']:
		raise StateError('You cannot reserve this name')
	try:
		NickAccount.query.filter(NickAccount.nick==p.name()).one()
	except NoResultFound:
		user = p.user
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
		User.query.filter(User.id==p.user.id).filter(User.password==args[0]).one()
	except NoResultFound:
		raise StateError('Incorrect password.')
	except MultipleResultsFound:
		pass
	else:
		if not isValidPassword(args[1], p.cn):
			raise ArgumentValueError('Invalid password')
		User.query.filter(User.id==p.user.id).update({ 'password': args[1] })
		session.commit()
		return

def setSimpleMaster(cn):
	p = player(cn)
	if sbserver.publicServer() == 1:
		p.message(error('This is not an open server, you need auth or master privileges to get master.'))
		return
	if currentAdmin() != None:
		p.message(error('Admin is present'))
		return
	if currentMaster() != None:
		p.message(error('Master is present'))
		return
	sbserver.setMaster(cn)

@eventHandler('player_setmaster')
def onSetMaster(cn, givenhash):
	p = player(cn)
	adminhash = sbserver.hashPassword(cn, sbserver.adminPassword())
	if givenhash == adminhash:
		sbserver.setAdmin(cn)
	else:
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
				p.login(na.user)
			else:
				if givenhash != adminhash:
					setSimpleMaster(cn)

@eventHandler('player_setmaster_off')
def onSetMasterOff(cn):
	sbserver.resetPrivilege(cn)

