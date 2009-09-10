from DB.db import dbmanager
from sqlalchemy.orm.exc import NoResultFound
from UserManager.usermanager import session, NickAccount, isLoggedIn, loggedInAs
from Bans.bans import ban
import sbserver, sbevents, sbtools

def warnNickReserved(cn, nickacct, count):
	if cn not in sbserver.clients():
		return
	nick = nickacct.nick
	if nick != sbserver.playerName(cn):
		onPlayerActive(cn)
		return
	if isLoggedIn(cn):
		user = loggedInAs(cn)
		if nickacct.user_id != user.id:
			ban(cn, 0, 'Use of reserved name')
		return
	if count > 4:
		ban(cn, 0, 'Use of reserved name')
		return
	remaining = 25-(count*5)
	sbserver.playerMessage(cn, sbtools.red('WARNING: ') + sbtools.blue('Your name is reserved. You have %i seconds to login or be kicked.' % remaining))
	sbevents.registerTimerHandler(5000, warnNickReserved, (cn, nickacct, count+1))

def onPlayerActive(cn):
	nick = sbserver.playerName(cn)
	try:
		nickacct = session.query(NickAccount).filter(NickAccount.nick==nick).one()
	except NoResultFound:
		return
	warnNickReserved(cn, nickacct, 0)

def onPlayerNameChanged(cn, new_name):
	onPlayerActive(cn)

def onReserveCommand(cn, args):
	if args != '':
		sbserver.playerMessage(sbtools.red('Usage: #reserve'))
		return
	nick = sbserver.playerName(cn)
	if not isLoggedIn(cn):
		sbserver.playerMessage(sbtools.red('You must be logged in to reserve your name.'))
		return
	user = loggedInAs(cn)
	if reserver(nick):
		sbserver.playerMessage(sbtools.red('Name is already reserved.'))
		return
	rn = ReservedNick(nick, user.id)
	session.add(rn)
	sbserver.playerMessage(cn, sbtools.green('Your account has been created.'))

sbevents.registerEventHandler('player_active', onPlayerActive)
sbevents.registerEventHandler('player_name_changed', onPlayerNameChanged)
sbevents.registerCommandHandler('reserve', onReserveCommand)

