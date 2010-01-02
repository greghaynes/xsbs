import asyncore
import socket
import logging
import collections
import time

class EventDispatcher(object):
	def __init__(self):
		self.handlers = {}
	def connect(self, event, handler):
		try:
			self.handlers[event].append(handler)
		except KeyError:
			self.handlers[event] = collections.deque()
			self.connect(event, handler)
	def trigger(self, event, *args):
		try:
			for handler in self.handlers[event]:
				try:
					handler(event, *args)
				except:
					logging.error('Unhandled exception in event handler for %s', event)
		except KeyError:
			pass

class IrcClient(asyncore.dispatcher):
	def __init__(self, serverinfo, clientinfo, use_logging=True):
		'''serverinfo is a tuple containing:
		      (hostname, port)
		   Clientinfo is a tuple containing:
		      (nickname, username, hostname, servername, realname)'''
		asyncore.dispatcher.__init__(self)
		self.use_logging = use_logging
		self.server_hostname = serverinfo[0]
		self.server_port = serverinfo[1]
		self.nick = clientinfo[0]
		self.username = clientinfo[1]
		self.hostname = clientinfo[2]
		self.servername = clientinfo[3]
		self.realname = clientinfo[4]
		self.events = EventDispatcher()
		self.is_connected = False
		self.channel_list = []
		self.throttle_size = 512
		self.trottle_time = 1
		self.part_message = 'PyAsyncirc Bot'
		self.events.connect('PING', self.handle_pong)
		self.events.connect('MODE', self.handle_mode)
		self.events.connect('PRIVMSG', self.handle_raw_privmsg)
	def logInfo(self, string):
		if(self.use_logging):
			logging.info(string)
	def doConnect(self):
		self.logInfo('Connecting to %s:%i' % (
				self.server_hostname,
				self.server_port))
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.bind((self.ip_address, 0))
		except AttributeError:
			pass
		self.connect((self.server_hostname, self.server_port))
		self.read_buffer = ''
		self.work_queue = collections.deque()
		self.throttle_timeout = time.time() + self.throttle_size
		self.throttle_used = 0
	def quit(self):
		self.send('QUIT :Bye\r\n')
		self.close()
		self.is_connected = False
	def handle_connect(self):
		self.work_queue.append('NICK :%s\r\n' % self.nick)
		self.work_queue.append('USER %s %s %s :%s\r\n' % (self.username, self.hostname, self.servername, self.realname))
	def handle_close(self):
		self.close()
		self.is_connected = False
	def handle_read(self):
		self.read_buffer += self.recv(4096)
		tmp_buff = self.read_buffer.split('\r\n')
		self.read_buffer = tmp_buff.pop()
		for line in tmp_buff:
			if line[0] == ':':
				args = line.split(' ')
				who = args[0][1:]
				event = args[1]
				args = line[len(who) + len(event) + 3:]
				self.events.trigger(event, who, args)
			else:
				event = line.split(' :')[0]
				args = line[len(event)+2:]
				self.events.trigger(event, args)
	def handle_write(self):
		data = self.work_queue.popleft()
		self.send(data)
	def writable(self):
		if time.time() >= self.throttle_timeout:
			self.throttle_timeout = time.time() + self.trottle_time
			self.throttle_used = 0
		try:
			if len(self.work_queue[0]) >= self.throttle_size:
				self.work_queue[0] = self.work_queue[0][:self.throttle_size]
		except IndexError:
			pass
		return len(self.work_queue) > 0 and len(self.work_queue[0]) + self.throttle_used < self.throttle_size
	def handle_pong(self, event, args):
		self.work_queue.append('PONG :%s\r\n' % args)
	def handle_mode(self, event, who, args):
		if not self.is_connected:
			self.is_connected = True
			for channel in self.channel_list:
				self.join(channel)
	def handle_ctcp(self, who_from, who_to, msg):
		pass
	def handle_privmsg(self, who_from, who_to, msg):
		pass
	def handle_raw_privmsg(self, event, who, args):
		to = args.split(' ', 1)[0]
		args = args[len(to)+2:]
		self.handle_privmsg(who, to, args)
	def join(self, channel):
		if self.is_connected:
			self.work_queue.append('JOIN :%s\r\n' % channel)
		else:
			self.channel_list.append(channel)
	def message(self, message, to):
		self.work_queue.append('PRIVMSG %s :%s\r\n' % (to, message))

def run(host, port, chan, nick):
	bot = IrcClient(
		(host, port),
		(nick, 'asyncirc', 'localhost', 'irc.gamesurge.net', 'asyncirc bot'))
	bot.doConnect()
	bot.join('#xsbs')
	asyncore.loop()

if __name__ == '__main__':
	server = "irc.gamesurge.net"
	nick = "asyncirc"
	password = "default"
	run(server, 6667, "#xsbs", nick)
