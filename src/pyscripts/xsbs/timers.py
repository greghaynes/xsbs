import sbserver

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
		self.update()
	def addTimer(self, delay, func, args=(), persistent=False):
		timer = Timer(self.currtime, delay, func, args, persistent)
		i = 0
		for iter in self.timers:
			if not iter.isTimedOut(timer.timeout):
				self.timers.insert(i, timer)
				return
			i += 1
		self.timers.append(timer)
	def update(self):
		self.currtime = sbserver.uptime()
		restarts = []
		i = 0
		for timer in self.timers:
			if timer.isTimedOut(self.currtime):
				timer()
				if timer.persistent:
					timer.reload()
					self.timers.pop(i)
					restarts.append(timer)
					i += 1
				else:
					del self.timers[i]
			else:
				break
		for timer in restarts:
			addTimer(timer.delay, timer.func, timer.args, timer.persistent)
			del timer

timermanager = TimerManager()

def addTimer(msecs, func, args=(), persistent=False):
	timermanager.addTimer(msecs, func, args, persistent)

def update():
	timermanager.update()

