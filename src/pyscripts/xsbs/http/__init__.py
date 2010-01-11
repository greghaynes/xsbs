import simpleasync
import asyncore
from xsbs.settings import PluginConfig

config = PluginConfig('httpserver')
enable = config.getOption('Config', 'enable', 'yes') == 'yes'
address = config.getOption('Config', 'ipaddress', '')
port = config.getOption('Config', 'port', '8081')
del config

port = int(port)

path_handlers = {}

def registerUrlHandler(url, func):
	path_handlers[url] = func

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
		try:
			path_handlers[self.path](self)
		except KeyError:
			self.respond_with(404, 'text/html', 0, '<html><body>Invalid URL</body></html>')
	def respond_with(self, code, type, length, data):
		if length <= 0:
			length = len(data)
		self.send_response(code)
		self.send_header("Content-type", type)
		self.send_header("Content-Length", length)
		self.end_headers()
		self.outgoing.append(data)
		self.outgoing.append(None)

if enable or __name__ == '__main__':
	server = simpleasync.Server(address, port, RequestHandler)
if __name__ == '__main__':
	asyncore.loop()

