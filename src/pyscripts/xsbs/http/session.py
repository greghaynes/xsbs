from xsbs.timers import addTimer

import time
import random
import hashlib

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
		self.randgen = random.Random()
		addTimer(2000, self.removeStales, (), True)
	def removeStales(self):
		cur_time = time.time()
		print 'checking sessions'
		for session in self.sessions.values():
			print session.key
			if (session.touch_time + self.stale_secs) < cur_time:
				del self.sessions[session.key]
		print ''

	def createSession(self):
		'''Create a session with a unique key
		   Returns newly created session'''
		sess = None
		while sess == None:
			testkey = hashlib.sha1(str(self.randgen.randint(0, 10000))).hexdigest()
			try:
				currsess = self.sessions[testkey]
			except KeyError:
				sess = Session(testkey)
				self.sessions[sess.key] = sess
		return sess

