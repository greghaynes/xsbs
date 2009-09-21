from xsbs.settings import PluginConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DatabaseManager:
	def __init__(self, uri):
		self.uri = uri
		self.isConnected = False
	def connect(self):
		if not self.isConnected:
			self.engine = create_engine(self.uri, echo=False)
			self.isConnected = True
			self.session = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)

config = PluginConfig('db')
uri = config.getOption('Config', 'uri', 'sqlite:///xsbs.db')
del config

dbmanager = DatabaseManager(uri)
dbmanager.connect()

