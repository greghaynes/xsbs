from xsbs.events import registerServerEventHandler
from xsbs.timers import addTimer
import sbserver
import asyncore
import socket

class MasterReg(asyncore.dispatcher):
	def __init__(self, hostname='sauerbraten.org', port=28787):
		asyncore.dispatcher.__init__(self)
		self.hostname = hostname
		self.port = port
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.buff = ''
		self.out_buff = []
		self.is_registered = False
		self.is_connected = False
		self.connect((self.hostname, self.port))
		self.register()
	def handle_close(self):
		self.is_connected = False
		print 'Master connection closed'
	def handle_connect(self):
		self.is_connected = True
		print 'Connected to master server'
		addTimer(3600000, self.update)
	def handle_write(self):
		for out in self.out_buff:
			self.send(out)
		del self.out_buff[:]
	def writable(self):
		return len(self.out_buff) > 0
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
	def register(self):
		self.out_buff.append('regserv %i\n' % sbserver.port())
	def update(self):
		if not self.is_connected:
			self.connect()
		self.register()

mr = MasterReg()

