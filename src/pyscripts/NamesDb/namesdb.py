from DB.db import dbmanager
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from xsbs.settings import PluginConfig
from xsbs.events import registerServerEventHandler
from xsbs.ui import error, info, insufficientPermissions
from xsbs.commands import registerCommandHandler
from UserPrivilege.userpriv import isPlayerMaster
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

def onNameChange(cn, newname):
	onConnect(cn)

def namesCmd(cn, args):
	if master_required and not isPlayerMaster(cn):
		insufficientPermissions(cn)
		return
	if args == '':
		sbserver.playerMessage(cn, error('Usage: #names <cn>'))
		return
	tcn = int(args)
	try:
		names = session.query(IpToNick).filter(IpToNick.ip==sbserver.playerIpLong(tcn)).all()
		if len(names) == 0:
			sbserver.playerMessage(cn, error('No names found'))
			return
	except NoResultFound:
		sbserver.playerMessage(cn, error('No names found'))
		return
	except ValueError:
		sbserver.playerMessage(cn, error('Invalid cn'))
		return
	namestr = 'Other known names: '
	for name in names:
		namestr += name.nick + ' '
	sbserver.playerMessage(cn, info(namestr))

def init():
	Base.metadata.create_all(dbmanager.engine)

init()
registerServerEventHandler('player_connect', onConnect)
registerServerEventHandler('player_name_changed', onNameChange)
registerCommandHandler('names', namesCmd)

