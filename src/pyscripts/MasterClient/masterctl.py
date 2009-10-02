from xsbs.events import registerServerEventHandler
from xsbs.timers import addTimer
from xsbs.ui import error, info, blue, orange
import sbserver
import asyncore
import socket

claimstr = orange('%s') + ' has claimed master as ' + blue('%s')

class MasterClient(asyncore.dispatcher):
	def __init__(self, hostname='sauerbraten.org', port=28787):
		asyncore.dispatcher.__init__(self)
		self.hostname = hostname
		self.port = port
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.buff = ''
		self.out_buff = []
		self.is_registered = False
		self.is_connected = False
		self.next_auth_id = 0
		self.auth_map = {}
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
			args = line.strip().split()
			key = args[0]
			if key == 'failreg':
				self.is_registered = False
				print 'Failed to register with master server'
			elif key == 'succreg':
				self.is_registered = True
				print 'Successfully registered with master server'
			elif key == 'chalauth':
				cn = self.auth_map[int(args[1])][0]
				chal = args[2]
				sbserver.authChallenge(cn, int(args[1]), chal)
			elif key == 'failauth':
				del self.auth_map[int(args[1])]
			elif key == 'succauth':
				authtup = self.auth_map[int(args[1])]
				cn = authtup[0]
				nick = sbserver.playerName(cn)
				authname = authtup[1]
				sbserver.setMaster(cn)
				sbserver.message(info(claimstr % (nick, authname)))
				del self.auth_map[int(args[1])]
	def register(self):
		self.out_buff.append('regserv %i\n' % sbserver.port())
	def update(self):
		if not self.is_connected:
			self.connect()
		self.register()
	def tryauth(self, cn, name):
		if not self.is_connected:
			sbserver.playerMessage(cn, error('Not connected to an authentication server'))
		else:
			self.auth_map[self.next_auth_id] = (cn, name)
			self.out_buff.append('reqauth %i %s\n' % (self.next_auth_id, name))
			self.next_auth_id += 1
	def anschal(self, id, val):
		if not self.is_connected:
			sbserver.playerMessage(cn, error('You should not be answering a challenge right now'))
		else:
			self.out_buff.append('confauth %i %s\n' % (id, val))

mc = MasterClient()
registerServerEventHandler('auth_try', mc.tryauth)
registerServerEventHandler('auth_ans', mc.anschal)

