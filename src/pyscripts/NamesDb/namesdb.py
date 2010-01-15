from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from xsbs.settings import PluginConfig
from xsbs.events import registerServerEventHandler
from xsbs.ui import error, info, insufficientPermissions
from xsbs.commands import commandHandler, UsageError
from xsbs.db import dbmanager
from xsbs.players import isAtLeastMaster
import sbserver

config = PluginConfig('namesdb')
tablename = config.getOption('Config', 'tablename', 'ip_name')
master_required = config.getOption('Config', 'master_required', 'no') == 'yes'
del config

Base = declarative_base()
session = dbmanager.session()

class IpToNick(Base):
	__tablename__=tablename
	id = Column(Integer, primary_key=True)
	ip = Column(Integer, index=True)
	nick = Column(String)
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

Base.metadata.create_all(dbmanager.engine)
registerServerEventHandler('player_connect', onConnect)
registerServerEventHandler('player_name_changed', onNameChange)

