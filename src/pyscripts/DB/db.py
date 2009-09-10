from ConfigParser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DatabaseManager:
	def __init__(self, uri):
		self.uri = uri
		self.isConnected = False
	def connect(self):
		if not self.isConnected:
			self.engine = create_engine(self.uri)
			self.isConnected = True
			self.session = sessionmaker(bind=self.engine)

uri = 'sqlite://xsbs.sql'

conf = ConfigParser()
conf.read('Config/db.conf')
if conf.has_option('Database', 'uri'):
	uri = conf.get('Database', 'uri')
dbmanager = DatabaseManager(uri)
dbmanager.connect()

del conf

