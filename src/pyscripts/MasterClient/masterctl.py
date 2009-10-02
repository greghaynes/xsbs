from xsbs.events import registerServerEventHandler
import asyncore

class MasterConn(asyncore.dispatcher):
	def __init__(self, hostname, port):
		asyncore.dispatcher.__init__(self)
		self.hostname = hostname
		self.port = port
		self.connect((hostname, port))
	def handle_close(self):
		pass

