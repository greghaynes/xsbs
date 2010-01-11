import asyncore, asynchat
import socket
import SimpleHTTPServer
import cStringIO
import traceback, sys
import logging

# Much of this cade is taken from http://code.activestate.com/recipes/259148/

class CI_dict(dict):
	"""Dictionary with case-insensitive keys
	Replacement for the deprecated mimetools.Message class
	"""
	def __init__(self, infile, *args):
		self._ci_dict = {}
		lines = infile.readlines()
		for line in lines:
			k,v=line.split(":",1)
			self._ci_dict[k.lower()] = self[k] = v.strip()
		self.headers = self.keys()
	def getheader(self,key,default=""):
		return self._ci_dict.get(key.lower(),default)
	def get(self,key,default=""):
		return self._ci_dict.get(key.lower(),default)
	def __getitem__(self,key):
		return self._ci_dict[key.lower()]
	def __contains__(self,key):
		return key.lower() in self._ci_dict

class RequestHandler(asynchat.async_chat,
	SimpleHTTPServer.SimpleHTTPRequestHandler):
	protocol_version = 'HTTP/1.1'
	MessageClass = CI_dict
	def __init__(self, connection, address, server):
		asynchat.async_chat.__init__(self, connection)
		self.client_address = address
		self.connection = connection
		self.server = server
		self.set_terminator('\r\n\r\n')
		self.rfile = cStringIO.StringIO()
		self.found_terminator = self.handle_request
		self.request_version = 'HTTP/1.1'
		self.wfile = cStringIO.StringIO()
	def collect_incoming_data(self, data):
		self.rfile.write(data)
	def handle_error(self):
		logging.error(traceback.print_exc(sys.stderr))
		self.close()
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
		self.handler = handler
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind((self.address, self.port))
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

if __name__=="__main__":
	port = 8081
	s=HttpServer('',port,RequestHandler)
	print "Running on port %s" %port
	try:
		asyncore.loop(timeout=2)
	except KeyboardInterrupt:
		print "Crtl+C pressed. Shutting down."

