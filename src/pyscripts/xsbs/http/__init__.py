import simpleasync
import asyncore

path_handlers = {}

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

