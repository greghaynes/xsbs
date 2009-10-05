from xsbs.events import registerServerEventHandler
from xsbs.timers import addTimer
from xsbs.colors import colordict
from xsbs.ui import error, info
from xsbs.settings import PluginConfig
from xsbs.net import ipLongToString
import sbserver
import asyncore
import socket
import logging
import string

config = PluginConfig('masterclient')
claimstr = config.getOption('Config', 'auth_message', '${green}${name}${white} has authenticated as ${magenta}${authname}')
master_host = config.getOption('Config', 'master_host', 'sauerbraten.org')
master_port = config.getOption('Config', 'master_port', '28787')
allow_auth = config.getOption('Config', 'allow_auth', 'yes') == 'yes'
del config
claimstr = string.Template(claimstr)
master_port = int(master_port)

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
		addTimer(60*60*1000, self.register, (), True)
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
				a = self.auth_map[int(args[1])]
				logging.info('%s (%s) failed to authenticate as %s' % (
					sbserver.playerName(a[0]), 
					ipLongToString(sbserver.playerIpLong(a[0])),
					a[1]))
				del self.auth_map[int(args[1])]
				self.close()
				self.is_connected = False
			elif key == 'succauth':
				authtup = self.auth_map[int(args[1])]
				logging.info('%s (%s) authenticated as %s' % (
					sbserver.playerName(authtup[0]), 
					ipLongToString(sbserver.playerIpLong(authtup[0])),
					authtup[1]))
				cn = authtup[0]
				nick = sbserver.playerName(cn)
				authname = authtup[1]
				msg = claimstr.substitute(colordict, name=nick, authname=authname)
				sbserver.message(info(msg))
				sbserver.setMaster(cn)
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
	def update(self):
		self.register()
	def tryauth(self, cn, name):
		if not allow_auth:
			sbserver.playerMessage(cn, error('Auth keys are disabled on this server'))
		self.do_connect()
		self.auth_map[self.next_auth_id] = (cn, name)
		self.out_buff.append('reqauth %i %s\n' % (self.next_auth_id, name))
		self.next_auth_id += 1
	def anschal(self, id, val):
		self.do_connect()
		self.out_buff.append('confauth %i %s\n' % (id, val))

mc = MasterClient(master_host, master_port)
registerServerEventHandler('auth_try', mc.tryauth)
registerServerEventHandler('auth_ans', mc.anschal)

