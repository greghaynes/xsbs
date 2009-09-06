import select

class SocketMonitor:
	def __init__(self):
		self.reads = {}
		self.writes = {}
		self.errors = {}
	def delRead(self, sock):
		self.reads.remove(sock)
	def onRead(self, sock, function, args, persist=False):
		self.reads[sock] = (function, args, persist)
	def onWrite(self, sock, function, args, persist=False):
		self.writes[sock] = (function, args, persist)
	def onError(self, sock, function, args, persist=False):
		self.errors[sock] = (function, args, persist)
	def pollOnce(self, timeout=0):
		i, o, e = select.select(self.reads.keys(), self.writes.keys(), self.errors.keys(), timeout)
		for sock in i:
			event = self.reads[sock]
			if not event[2]:
				del self.reads[sock]
			event[0](*event[1])
		for sock in o:
			event = self.writes[sock]
			if not event[2]:
				self.writes.remove(sock)
			event[0](*event[1])
		for sock in e:
			event = self.errors[sock]
			if not event[2]:
				self.errors.remove(sock)
			event[0](*event[1])

