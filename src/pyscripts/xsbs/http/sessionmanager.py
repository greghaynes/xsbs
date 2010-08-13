import time

class Session(dict):
	def __init__(self, key):
		self.key = key
		self.create_time = time.time()
		self.touch_time = self.create_time
	def touch(self):
		self.touch_time = time.time()

class SessionManager(object):
	def __init__(self, stale_secs=3600):
		self.sessions = {}
		self.stale_secs = stale_secs
	def removeStales(self):
		cur_time = time.time()
		for session in self.sessions.values():
			if (session.touch_time + self.stale_secs) < cur_time:
				del self.sessions[session.key]

