from xsbs.events import registerServerEventHandler, triggerServerEvent
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
register_interval = config.getOption('Config', 'register_interval', '3600')
del config
claimstr = string.Template(claimstr)
master_port = int(master_port)
register_interval = int(register_interval)

class Request:
	def __init__(self, data):
		self.data = data
		self.is_running = False
	def do(self, *args):
		if not self.is_running:
			args[0].send(self.data)
			self.is_running = True

class AuthRequest(Request):
	def __init__(self, id, cn, name):
		Request.__init__(self, 'reqauth %i %s\n' % (id, name))
		self.id = id
		self.cn = cn
		self.name = name

class AuthManager:
	def __init__(self):
		self.attempts = []
		self.id = 0
	def getAuth(self, id):
		for auth in self.attempts:
			if auth.id == id:
				return auth
		raise ValueError('Non existent auth request id')
	def request(self, cn, name):
		req = AuthRequest(self.id, cn, name)
		self.attempts.append(req)
		self.id += 1
		return req
	def challenge(self, id, chal):
		auth = self.getAuth(id)
		sbserver.authChallenge(auth.cn, auth.id, chal)
	def challengeResponse(self, id, response):
		auth = self.getAuth(id)
		return Request('confauth %i %s\n' % (id, response))
	def delAuth(self, id):
		i = 0
		for auth in self.attempts:
			if auth.id == id:
				del self.attempts[i]
				return
			i += 1
		raise ValueError('Non existent auth reqest id')

class MasterClient(asyncore.dispatcher):
	def __init__(self, hostname='sauerbraten.org', port=28787):
		asyncore.dispatcher.__init__(self)
		self.hostname = hostname
		self.port = port
		self.request_queue = []
		self.responses_needed = 0
		self.read_buff = ''
		self.authman = AuthManager()
		self.do_connect = True
		self.register()
	def makeRequest(self, request):
		if self.do_connect:
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
			if sbserver.ip():
				self.bind((sbserver.ip(), 0))
			self.connect((self.hostname, self.port))
			self.do_connect = False
		self.request_queue.append(request)
	def try_auth(self, cn, name):
		self.makeRequest(self.authman.request(cn, name))
	def challenge_response(self, cn, id, response):
		self.makeRequest(self.authman.challengeResponse(id, response))
	def register(self):
		addTimer(register_interval*1000, self.register)
		self.makeRequest(Request('regserv %i\n' % sbserver.port()))
	def handle_response(self, response):
		args = response.split(' ')
		key = args[0]
		response_end = True
		if key == 'succreg':
			logging.info('Master server registration succeded')
			triggerServerEvent('master_registration_succeeded', ())
		elif key == 'failreg':
			logging.warning('Master server registration failed')
			triggerServerEvent('master_registration_failed', ())
		elif key == 'succauth':
			auth = self.authman.getAuth(int(args[1]))
			triggerServerEvent('player_auth_succeed', (auth.cn, auth.name))
			self.authman.delAuth(auth.id)
		elif key == 'failauth':
			auth = self.authman.getAuth(int(args[1]))
			triggerServerEvent('player_auth_fail', (auth.cn, auth.name))
			self.authman.delAuth(auth.id)
		elif key == 'chalauth':
			response_end = False
			self.authman.challenge(int(args[1]), args[2])
		if self.responses_needed == 0:
			logging.error('Got response when none needed')
		else:
			self.responses_needed -= 1
		if response_end:
			if self.responses_needed == 0:
				self.close()
				self.do_connect = True
	def handle_connect(self):
		logging.debug('Connected to master server')
	def handle_write(self):
		item = self.request_queue.pop(0)
		self.send(item.data)
		self.responses_needed += 1
	def handle_close(self):
		self.do_connect = True
	def handle_read(self):
		self.read_buff += self.recv(4096)
		tmp_buff = self.read_buff.split('\n')
		self.read_buff = tmp_buff.pop()
		for line in tmp_buff:
			self.handle_response(line)
	def writable(self):
		return len(self.request_queue) > 0

mc = MasterClient(master_host, master_port)
registerServerEventHandler('player_auth_request', mc.try_auth)
registerServerEventHandler('player_auth_challenge_response', mc.challenge_response)

