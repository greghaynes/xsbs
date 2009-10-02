from xsbs.events import registerServerEventHandler
from xsbs.timers import addTimer
import sbserver
import asyncore
import socket

class MasterConn(asyncore.dispatcher):
	def __init__(self, hostname='sauerbraten.org', port=28787):
		asyncore.dispatcher.__init__(self)
		self.hostname = hostname
		self.port = port
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect((hostname, port))
		self.buff = ''
		self.do_reg = True
		self.is_registered = False
	def handle_close(self):
		print 'Master connection closed'
	def handle_connect(self):
		print 'Connected to master server'
	def handle_write(self):
		if self.do_reg:
			self.send('regserv %i\n' % sbserver.port())
			self.do_reg = False
	def writable(self):
		return self.do_reg
	def handle_read(self):
		self.buff += self.recv(4096)
		tmp_buff = self.buff.split('\n')
		self.buff = tmp_buff.pop()
		for line in tmp_buff:
			key = line.strip().split()[0]
			if key == 'failreg':
				self.is_registered = False
				print 'Failed to register with master server'
				self.close()
			elif key == 'succreg':
				self.is_registered = True
				print 'Successfully registered with master server'
				self.close()

def updateMaster():
	mc = MasterConn()
	addTimer(3600000, updateMaster)

updateMaster()

