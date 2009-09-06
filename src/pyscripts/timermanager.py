class TimerManager():
	def __init__(self, currmsecs):
		self.currmsecs = currmsecs
		self.timers = []
	def addTimer(self, msecs, func, args):
		i = 0
		nt = [msecs + self.currmsecs, func, args]
		if len(self.timers) == 0:
			self.timers.append(nt)
			return
		for timer in self.timers:
			if timer[0] < nt[0]:
				self.timers.insert(i, nt)
			i += 1
	def setTime(self, msecs):
		if self.currmsecs == 0:
			for timer in self.timers:
				timer[0] = timer[0] + msecs
		self.currmsecs = msecs
		i = 0
		for timer in self.timers:
			if timer[0] < self.currmsecs:
				del self.timers[i]
				timer[1](*timer[2])
			else:
				return
			i += 1
