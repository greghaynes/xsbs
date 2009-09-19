from DB.db import dbmanager
from sqlalchemy.orm.exc import NoResultFound
from UserManager.usermanager import session, NickAccount, isLoggedIn, loggedInAs
from Bans.bans import ban
import sbserver
from xsbs.events import registerServerEventHandler
from xsbs.commands import registerCommandHandler
from xsbs.timers import addTimer
from xsbs.colors import red, blue
from xsbs.players import player

def warnNickReserved(cn, count, sessid):
	try:
		p = player(cn)
		nickacct = p.warn_nickacct
		if nickacct.nick != sbserver.playerName(cn):
			return
		if sessid != sbserver.playerSessionId(cn):
			return
	except (AttributeError, ValueError):
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
	sbserver.playerMessage(cn, red('WARNING: ') + blue('Your name is reserved. You have %i seconds to login or be kicked.' % remaining))
	addTimer(5000, warnNickReserved, (cn, count+1, sessid))

def nickReserver(nick):
	return session.query(NickAccount).filter(NickAccount.nick==nick).one()

def onPlayerActive(cn):
	nick = sbserver.playerName(cn)
	try:
		nickacct = nickReserver(sbserver.playerName(cn))
	except NoResultFound:
		return
	p = player(cn)
	p.warn_nickacct = nickacct
	warnNickReserved(cn, 0, sbserver.playerSessionId(cn))

def onPlayerNameChanged(cn, new_name):
	onPlayerActive(cn)

def onReserveCommand(cn, args):
	if args != '':
		sbserver.playerMessage(red('Usage: #reserve'))
		return
	nick = sbserver.playerName(cn)
	if not isLoggedIn(cn):
		sbserver.playerMessage(red('You must be logged in to reserve your name.'))
		return
	user = loggedInAs(cn)
	if reserver(nick):
		sbserver.playerMessage(red('Name is already reserved.'))
		return
	rn = ReservedNick(nick, user.id)
	session.add(rn)
	sbserver.playerMessage(cn, green('Your account has been created.'))

registerServerEventHandler('player_active', onPlayerActive)
registerServerEventHandler('player_name_changed', onPlayerNameChanged)
registerCommandHandler('reserve', onReserveCommand)

