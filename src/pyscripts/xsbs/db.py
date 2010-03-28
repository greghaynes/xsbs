from xsbs.settings import PluginConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, InvalidRequestError

class DatabaseManager:
	def __init__(self, uri):
		self.uri = uri
		self.isConnected = False
	def connect(self):
		if not self.isConnected:
			self.engine = create_engine(self.uri, echo=False)
			self.isConnected = True
			self.m_session = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)()
	def reconnect(self):
		self.isConnected = False
		del self.m_session
		del self.engine
		self.connect()
	def session(self):
		return self.m_session
	def query(self, *args, **kwargs):
		try:
			q = self.session().query(*args, **kwargs)
		except (OperationalError, InvalidRequestError):
			self.reconnect()
			q = self.session().query(*args, **kwargs)
		return q

config = PluginConfig('db')
uri = config.getOption('Config', 'uri', 'sqlite:///xsbs.db')
del config

dbmanager = DatabaseManager(uri)
dbmanager.connect()

