import asyncore, asynchat
import socket
import SimpleHttpServer
import cStringIO
import logging

class RequestHandler(asynchat.async_chat,
	SimpleHttpServer.SimpleHttpRequestHandler):
	protocol_version = 'HTTP/1.0'
	def __init__(self, connection, address, server):
		asynchat.async_chat.__init__(self, connection)
		self.client_address = address
		self.connection = connection
		self.server = server
		self.set_terminator('\r\n\r\n')
		self.rfile = cStringIO.StringIO()
		self.found_terminator = self.handle_request
		self.request_version = 'HTTP/1.0'
		self.wfile = cStringIO.StringIO()
	def collect_incoming_data(self, data):
		self.rfile.write(data)
	def handle_request(self):
		self.rfile.seek(0)
		self.raw_requestline = self.rfile.readline()
		self.parse_request()
		if self.command in ['GET', 'HEAD']:
			method = 'do_' + self.command
			if hasattr(self,method):
				getattr(self,method)()
				self.finish()
		elif self.command=="POST":
			self.prepare_POST()
		else:
			self.send_error(501, "Unsupported method (%s)" %self.command)
	def do_GET(self):
		pass
	def do_POST(self):
		pass

class HttpServer(asyncore.dispatcher):
	def __init__(self, address, port, handler):
		asyncore.dispatcher.__init__(self)
		self.address = address
		self.port = port
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind(self.address, self.port)
		self.listen(5)
	def handle_accept(self):
		try:
			conn, addr = self.accept()
		except socket.error:
			logging.error('Accept threw error')
		except TypeError:
			logging.error('Accept threw EWOULDBLOCK')
		else:
			self.handler(conn, addr, self)

