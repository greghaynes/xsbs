import sbserver
import logging

class Timer:
	def __init__(self, currtime, delay, func, args=(), persistent=False):
		self.delay = delay
		self.func = func
		self.args = args
		self.persistent = persistent
		self.timeout = currtime + delay
	def __call__(self):
		self.func(*self.args)
	def isTimedOut(self, time):
		return time >= self.timeout
	def reload(self, currtime):
		self.timeout = self.delay + currtime

class TimerManager:
	def __init__(self):
		self.timers = []
		self.is_executing = False
		self.add_queue = []
		self.update()
	def addTimer(self, delay, func, args=(), persistent=False):
		if self.is_executing:
			self.add_queue.append((delay, func, args, persistent))
		else:
			timer = Timer(self.currtime, delay, func, args, persistent)
			i = 0
			for iter in self.timers:
				if not iter.isTimedOut(timer.timeout):
					self.timers.insert(i, timer)
					return
				i += 1
			self.timers.append(timer)
	def update(self):
		for timer in self.add_queue:
			self.addTimer(*timer)
		del self.add_queue[:]
		self.is_executing = True
		self.currtime = sbserver.uptime()
		while True:
			try:
				if self.timers[0].isTimedOut(self.currtime):
					timer = self.timers.pop(0)
					try:
						timer()
					except:
						logging.error('Uncaught exception while executing timer method.')
					if timer.persistent:
						self.addTimer(timer.delay, timer.func, timer.args, timer.persistent)
				else:
					break
			except IndexError:
				break
		self.is_executing = False

timermanager = TimerManager()

def addTimer(msecs, func, args=(), persistent=False):
	timermanager.addTimer(msecs, func, args, persistent)

def update():
	timermanager.update()

