import select

class SocketMonitor:
	def __init__(self):
		self.reads = {}
		self.writes = {}
		self.errors = {}
	def onRead(self, sock, function, args):
		self.reads[sock] = (function, args)
	def onWrite(self, sock, function, args):
		self.writes[sock] = (function, args)
	def onError(self, sock, function, args):
		self.errors[sock] = (function, args)
	def pollOnce(self, timeout=0):
		i, o, e = select.select(self.reads.keys(), self.writes.keys(), self.errors.keys(), timeout)
		for sock in i:
			event = self.reads[sock]
			self.reads.remove(sock)
			event[0](*event[1])
		for sock in o:
			event = self.writes[sock]
			self.writes.remove(sock)
			event[0](*event[1])
		for sock in e:
			event = self.errors[sock]
			self.errors.remove(sock)
			event[0](*event[1])

