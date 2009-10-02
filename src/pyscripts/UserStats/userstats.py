import sbserver
from xsbs.players import player
from xsbs.settings import PluginConfig
from xsbs.events import registerServerEventHandler
from DB.db import dbmanager
from UserManager.usermanager import loggedInAs
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
import time

config = PluginConfig('userstats')
statstable = config.getOption('Config', 'tablename', 'userstats')
tkill_fragval = int(config.getOption('Values', 'teamkill_fragval', '0'))
tkill_deathval = int(config.getOption('Values', 'teamkill_deathval', '0'))
suicide_fragval = int(config.getOption('Values', 'suicide_fragval', '0'))
suicide_deathval = int(config.getOption('Values', 'suicide_deathval', '1'))
del config

Base = declarative_base()
session = dbmanager.session()

class UserSessionStats(Base):
	'A session is at most a game length.'
	__tablename__ = statstable
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer)
	end_time = Column(Integer)
	frags = Column(Integer)
	deaths = Column(Integer)
	teamkills = Column(Integer)
	def __init__(self, user_id, end_time, frags, deaths, teamkills):
		self.user_id = user_id
		self.end_time = end_time
		self.frags = frags
		self.deaths = deaths
		self.teamkills = teamkills

def flushPlayerSession(cn):
	user = loggedInAs(cn)
	UserSessionStats(cn)

def onConnect(cn):
	player(cn).stats_frags = 0
	player(cn).stats_deaths = 0
	player(cn).stats_teamkills = 0

def onFrag(cn, tcn):
	if cn == tcn:
		val = suicide_fragval
	else:
		val = 1
	try:
		player(cn).stats_frags += val
	except AttributeError:
		player(cn).stats_frags = val

def onTeamKill(cn, tcn):
	print 'teamkill'

registerServerEventHandler('player_frag', onFrag)
registerServerEventHandler('player_teamkill', onTeamKill)

