import simpleasync
import asyncore

path_handlers = {}

def registerUrlHandler(url, func):
	path_handlers[url] = func

class urlHandler(object):
	def __init__(self, url):
		self.url = name
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
			self.send_response(404)
			self.end_headers()
			self.outgoing.append('Invalid URL')
			self.outgoing.append(None)

server = simpleasync.Server('', 8081, RequestHandler)
if __name__=="__main__":
	asyncore.loop()

