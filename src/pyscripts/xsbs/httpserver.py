import asyncore, asynchat
import socket
import SimpleHttpServer
import cStringIO
import traceback, os
import logging

class CaseInsensitiveDict:
    """
	Taken from http://code.activestate.com/recipes/66315/

	Dictionary, that has case-insensitive keys.

	Keys are retained in their original form
	when queried with .keys() or .items().

	Implementation: An internal dictionary maps lowercase
	keys to (key,value) pairs. All key lookups are done
	against the lowercase keys, but all methods that expose
	keys to the user retrieve the original keys."""
	def __init__(self, dict=None):
		"""Create an empty dictionary, or update from 'dict'."""
		self._dict = {}
		if dict:
			self.update(dict)
	def __getitem__(self, key):
		"""Retrieve the value associated with 'key' (in any case)."""
		k = key.lower()
		return self._dict[k][1]
	def __setitem__(self, key, value):
		"""Associate 'value' with 'key'. If 'key' already exists, but
		in different case, it will be replaced."""
		k = key.lower()
		self._dict[k] = (key, value)
	def has_key(self, key):
		"""Case insensitive test wether 'key' exists."""
		k = key.lower()
		return self._dict.has_key(k)
	def keys(self):
		"""List of keys in their original case."""
		return [v[0] for v in self._dict.values()]
	def values(self):
		"""List of values."""
		return [v[1] for v in self._dict.values()]
	def items(self):
		"""List of (key,value) pairs."""
		return self._dict.values()
	def get(self, key, default=None):
		"""Retrieve value associated with 'key' or return default value
		if 'key' doesn't exist."""
		try:
			return self[key]
		except KeyError:
			return default
	def setdefault(self, key, default):
		"""If 'key' doesn't exists, associate it with the 'default' value.
		Return value associated with 'key'."""
		if not self.has_key(key):
			self[key] = default
		return self[key]
	def update(self, dict):
		"""Copy (key,value) pairs from 'dict'."""
		for k,v in dict.items():
			self[k] = v
	def __repr__(self):
		"""String representation of the dictionary."""
		items = ", ".join([("%r: %r" % (k,v)) for k,v in self.items()])
		return "{%s}" % items
	def __str__(self):
		"""String representation of the dictionary."""
		return repr(self)

class RequestHandler(asynchat.async_chat,
	SimpleHttpServer.SimpleHttpRequestHandler):
	protocol_version = 'HTTP/1.1'
	MessageClass = CaseInsensitiveDict
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

