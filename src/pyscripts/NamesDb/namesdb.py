from elixir import Entity, Field, Integer, String, Boolean, ManyToOne, OneToMany, session
from sqlalchemy.orm.exc import NoResultFound

from xsbs.settings import PluginConfig
from xsbs.events import eventHandler
from xsbs.ui import error, info, insufficientPermissions
from xsbs.commands import commandHandler, UsageError
from xsbs.players import isAtLeastMaster

import sbserver

config = PluginConfig('namesdb')
master_required = config.getOption('Config', 'master_required', 'no') == 'yes'
del config

class IpToNick(Entity):
	ip = Field(Integer, index=True)
	nick = Field(String(15))
	def __init__(self, ip, nick):
		self.ip = ip
		self.nick = nick

@eventHandler('player_connect')
def onConnect(cn):
	try:
		same = session.query(IpToNick).filter(IpToNick.ip==sbserver.playerIpLong(cn)).filter(IpToNick.nick==sbserver.playerName(cn)).all()
		if len(same) > 0:
			return
	except NoResultFound:
		pass
	ent = IpToNick(sbserver.playerIpLong(cn), sbserver.playerName(cn))
	session.add(ent)
	session.commit()

@eventHandler('player_name_changed')
def onNameChange(cn, oldname, newname):
	onConnect(cn)

@commandHandler('names')
def namesCmd(p, args):
	'''@description Display names used by client
	   @usage cn
	   @public'''
	if master_required and not isAtLeastMaster(p.cn):
		insufficientPermissions(p.cn)
		return
	if args == '':
		raise UsageError()
		return
	try:
		tcn = int(args)
		names = session.query(IpToNick).filter(IpToNick.ip==sbserver.playerIpLong(tcn)).all()
		if len(names) == 0:
			p.message(info('No names found'))
			return
	except NoResultFound:
		p.message(info('No names found'))
		return
	except ValueError:
		p.message(error('Invalid cn'))
		return
	namestr = 'Other known names: '
	for name in names:
		namestr += name.nick + ' '
	p.message(info(namestr))

