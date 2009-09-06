class TimerManager():
	def __init__(self, currmsecs):
		self.currmsecs = currmsecs
		self.timers = []
	def addTimer(self, msecs, func, args):
		i = 0
		nt = (msecs + self.currmsecs, func, args)
		for timer in self.timers:
			if timer[0] < nt[0]:
				self.timers.insert(i, x)
			i += 1
	def setTime(self, msecs):
		self.currmsecs = msecs
		for timer in self.timers:
			if timer[0] < self.currmsecs:
				timer[1](*timer[2])
			else:
				return
