import simpleasync
import asyncore
import re
from xsbs.settings import PluginConfig
from UserManager.usermanager import userAuth
from UserPrivilege.userpriv import isMaster as isUserMaster

config = PluginConfig('httpserver')
enable = config.getOption('Config', 'enable', 'yes') == 'yes'
address = config.getOption('Config', 'ipaddress', '')
port = config.getOption('Config', 'port', '8081')
del config

port = int(port)

path_handlers = {}
regex_path_handlers = []

def registerRegexUrlHandler(regex, func):
	regex_path_handlers.append((re.compile(regex), func))

def registerUrlHandler(url, func):
	path_handlers[url] = func

def isMaster(email, password):
	user = userAuth(email, password)
	if user:
		val = isUserMaster(user.id)
		del user
		return val
	else:
		return False

class regexUrlHandler(object):
	def __init__(self, url):
		self.url = url
	def __call__(self, f):
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		registerRegexUrlHandler(self.url, f)
		return f

class urlHandler(object):
	def __init__(self, url):
		self.url = url
	def __call__(self, f):
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		registerUrlHandler(self.url, f)
		return f

class RequestHandler(simpleasync.RequestHandler):
	def __init__(self, conn, addr, server):
		simpleasync.RequestHandler.__init__(self, conn, addr, server)
	def handle_data(self):
		print self.path
		try:
			handler = path_handlers[self.path]
		except KeyError:
			for exph in regex_path_handlers:
				m = exph[0].match(self.path)
				if m:
					exph[1](self, **m.groupdict())
			self.respond_with(404, 'text/html', 0, '<html><body>Invalid URL</body></html>')
		else:
			handler(self)
	def respond_with(self, code, type, length, data):
		if length <= 0:
			length = len(data)
		self.send_response(code)
		self.send_header("Access-Control-Allow-Origin", "*")
		self.send_header('Connection', 'close')
		self.send_header('Content-type', type)
		self.send_header('Content-Length', length)
		self.end_headers()
		self.outgoing.append(data)
		self.outgoing.append('\r\n')
		self.outgoing.append(None)

if enable or __name__ == '__main__':
	server = simpleasync.Server(address, port, RequestHandler)
if __name__ == '__main__':
	asyncore.loop()

