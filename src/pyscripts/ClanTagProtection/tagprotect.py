from xsbs.events import registerServerEventHandler
from xsbs.players import player
from UserManager.usermanager import User
from NickReserve.nickreserve import nickReserver
import sbserver
from DB.db import dbmanager
from sqlalchemy.orm import relation
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
import re

regex = '\[.{1,5}\]|<.{1,5}>|\{.{1,5}\}|\}.{1,5}\{|.{1,5}\||\|.{1,5}\|'
regex = re.compile(regex)

Base = declarative_base()
session = dbmanager.session()

class ClanTag(Base):
	__tablename__ = 'clantags'
	id = Column(Integer, primary_key=True)
	tag = Column(String)
	def __init__(self, tag):
		self.tag = tag

class ClanMember(Base):
	__tablename__ = 'clanmember'
	id = Column(Integer, primary_key=True)
	tag_id = Column(Integer)
	user_id = Column(Integer)
	tag = relation(ClanTag, primaryjoin=tag_id=ClanTag.id)
	user = relation(User, primaryjoin=user_id=User.id)
	def __init__(self, tag_id, user_id):
		self.tag_id = tag_id
		self.user_id = user_id

def isProtected(nick):
	potentials = []
	matches = regex.findall(nick)
	for match in matches:
		potentials.append(match)

def onConnect(cn):
	isProtected(sbserver.playerName(cn))

def onNameChange(cn, name):
	onConnect(cn)

registerServerEventHandler('player_connect_delayed', onConnect)
registerServerEventHandler('player_name_changed', onNameChange)

