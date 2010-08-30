from xsbs.commands import commandHandler, UsageError, StateError, ArgumentValueError
from xsbs.ui import info, error, warning

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


