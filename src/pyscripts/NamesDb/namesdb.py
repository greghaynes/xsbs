from elixir import Entity, Field, Integer, String, Boolean, ManyToOne, OneToMany, session

from xsbs.settings import PluginConfig
from xsbs.events import registerServerEventHandler
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

def onNameChange(cn, oldname, newname):
	onConnect(cn)

@commandHandler('names')
def namesCmd(cn, args):
	'''@description Display names used by client
	   @usage cn
	   @public'''
	if master_required and not isAtLeastMaster(cn):
		insufficientPermissions(cn)
		return
	if args == '':
		raise UsageError()
		return
	try:
		tcn = int(args)
		names = session.query(IpToNick).filter(IpToNick.ip==sbserver.playerIpLong(tcn)).all()
		if len(names) == 0:
			sbserver.playerMessage(cn, info('No names found'))
			return
	except NoResultFound:
		sbserver.playerMessage(cn, info('No names found'))
		return
	except ValueError:
		sbserver.playerMessage(cn, error('Invalid cn'))
		return
	namestr = 'Other known names: '
	for name in names:
		namestr += name.nick + ' '
	sbserver.playerMessage(cn, info(namestr))

registerServerEventHandler('player_connect', onConnect)
registerServerEventHandler('player_name_changed', onNameChange)

