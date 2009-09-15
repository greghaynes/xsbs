import sbevents
from xsbs.asynclient import LineConnection

class HttpRequest(LineConnection):
	def __init__(self, hostname, port=80):
		LineConnection.__init__(self, hostname, port)
		self.path = '/'
		self.port = 80
		self.isConnected = False
	def __call__(self):
		if self.hostname == '':
			raise ValueError('Invalid hostname')
	def write(self):
		self.setWatchWrite(False)
		if not self.isConnected:
			self.setWatchRead(True)

