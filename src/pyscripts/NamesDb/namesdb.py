from DB.db import dbmanager
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from xsbs.settings import PluginConfig
from xsbs.events import registerServerEventHandler
from xsbs.ui import error, info
from xsbs.commands import registerCommandHandler
import sbserver

config = PluginConfig('namesdb')
tablename = config.getOption('Config', 'tablename', 'ip_name')

Base = declarative_base()
session = dbmanager.session()

class IpToNick(Base):
	__tablename__=tablename
	id = Column(Integer, primary_key=True)
	ip = Column(Integer)
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
	print 'inserting'
	ent = IpToNick(sbserver.playerIpLong(cn), sbserver.playerName(cn))
	session.add(ent)
	session.commit()

def onNameChange(cn):
	onConnect(cn)

def namesCmd(cn, args):
	if args == '':
		sbserver.playerMessage(cn, error('Usage: #names <cn>'))
		return
	tcn = int(args)
	try:
		names = session.query(IpToNick).filter(IpToNick.ip==sbserver.playerIpLong(cn)).all()
		if len(names) == 0:
			sbserver.playerMessage(cn, error('No names found'))
			return
	except NoResultFound:
		sbserver.playerMessage(cn, error('No names found'))
		return
	namestr = 'Other known names: '
	for name in names:
		namestr += name.nick
	sbserver.playerMessage(cn, info(namestr))

def init():
	Base.metadata.create_all(dbmanager.engine)

init()
registerServerEventHandler('player_connect', onConnect)
registerCommandHandler('names', namesCmd)

