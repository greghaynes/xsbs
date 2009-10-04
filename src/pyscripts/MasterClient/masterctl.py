from xsbs.events import registerServerEventHandler
from xsbs.timers import addTimer
from xsbs.colors import colordict
from xsbs.ui import error, info
from xsbs.settings import PluginConfig
import sbserver
import asyncore
import socket
import logging
import string

config = PluginConfig('masterclient')
claimstr = config.getOption('Config', 'auth_message', '${green}${name}${white} has claimed master as ${magenta}${authname}')
del config
claimstr = string.Template(claimstr)

class MasterClient(asyncore.dispatcher):
	def __init__(self, hostname='sauerbraten.org', port=28787):
		asyncore.dispatcher.__init__(self)
		self.hostname = hostname
		self.port = port
		self.buff = ''
		self.out_buff = []
		self.is_registered = False
		self.is_connected = False
		self.is_connecting = False
		self.reg_in_progress = False
		self.next_auth_id = 0
		self.auth_map = {}
		self.register()
	def handle_close(self):
		self.is_connected = False
		self.is_connecting = False
		self.close()
	def handle_connect(self):
		self.is_connected = True
		self.is_connecting = False
		logging.debug('Connected to master server')
	def handle_write(self):
		for out in self.out_buff:
			self.send(out)
		del self.out_buff[:]
	def writable(self):
		return len(self.out_buff) > 0
	def do_connect(self):
		if not self.is_connected and not self.is_connecting:
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
			if sbserver.ip():
				self.bind((sbserver.ip(), 0))
			self.connect((self.hostname, self.port))
			self.is_connecting = True
	def handle_read(self):
		self.buff += self.recv(4096)
		tmp_buff = self.buff.split('\n')
		self.buff = tmp_buff.pop()
		for line in tmp_buff:
			args = line.strip().split()
			key = args[0]
			if key == 'failreg':
				self.is_registered = False
				logging.warning('Failed to register with master server: %s' % line[8:])
				self.is_connected = False
				self.is_connecting = False
				self.reg_in_progress = False
				self.close()
			elif key == 'succreg':
				self.is_registered = True
				logging.info('Successfully registered with master server')
				self.reg_in_progress = False
				self.is_connecting = False
				self.is_connected = False
				self.close()
			elif key == 'chalauth':
				cn = self.auth_map[int(args[1])][0]
				chal = args[2]
				sbserver.authChallenge(cn, int(args[1]), chal)
			elif key == 'failauth':
				del self.auth_map[int(args[1])]
				self.close()
				self.is_connected = False
			elif key == 'succauth':
				authtup = self.auth_map[int(args[1])]
				cn = authtup[0]
				nick = sbserver.playerName(cn)
				authname = authtup[1]
				sbserver.setMaster(cn)
				msg = claimstr.substitute(colordict, name=nick, authname=authname)
				sbserver.message(info(msg))
				del self.auth_map[int(args[1])]
				self.is_connected = False
				self.close()
	def register(self):
		if self.reg_in_progress:
			logging.debug('Registration already in progress')
			return
		self.do_connect()
		logging.info('Attempting to register with master server')
		self.out_buff.append('regserv %i\n' % sbserver.port())
		self.reg_in_progress = True
		addTimer(60*60*1000, self.register, (), True)
	def update(self):
		self.register()
	def tryauth(self, cn, name):
		self.do_connect()
		self.auth_map[self.next_auth_id] = (cn, name)
		self.out_buff.append('reqauth %i %s\n' % (self.next_auth_id, name))
		self.next_auth_id += 1
	def anschal(self, id, val):
		self.do_connect()
		self.out_buff.append('confauth %i %s\n' % (id, val))

mc = MasterClient()
registerServerEventHandler('auth_try', mc.tryauth)
registerServerEventHandler('auth_ans', mc.anschal)

