import sbevents
import socket

class Connection:
	def __init__(self, hostname, port):
		self.hostname = hostname
		self.port = port
		self.socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	def __del__(self):
		if self.socket != None:
			for op in [sbevents.sockmon.delRead, sbevents.sockmon.delWrite, sbevents.sockmon.delError]:
				try:
					op(self.socket)
				except ValueError:
					pass
			self.socket.close()
	def connect(self):
		try:
			self.socket.connect((self.hostname, self.port))
		except socket.error:
			pass
	def setWatchRead(self, val):
		if val:
			sbevents.onRead(self.socket, self.read, (), True)
		else:
			sbevents.delRead(self.socket)
	def setWatchWrite(self, val):
		if val:
			sbevents.onWrite(self.socket, self.write, (), True)
		else:
			sbevents.delWrite(self.socket)
	def setWatchError(self, val):
		if val:
			sbevents.onError(self.socket, self.error, (), True)
		else:
			sbevents.delError(self.socket)
	def read(self):
		pass
	def write(self):
		pass
	def error(self):
		pass

class LineConnection(Connection):
	def __init__(self, hostname, port):
		Connection.__init__(self, hostname, port)
		self.read_size = 4096
		self.buffer = ''
	def read(self):
		self.buffer += self.socket.recv(self.read_size)
		lines = self.buffer.strip().split()
		self.buffer = lines.pop()
		self.readLines(lines)
	def readLines(self, lines):
		pass

