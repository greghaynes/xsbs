from twisted.internet.task import LoopingCall
from twisted.internet import reactor

def addTimer(msecs, func, args=(), persistent=False):
	if not persistent:
		reactor.callLater(msecs / 1000, func, *args)
	else:
		call = LoopingCall(func, *args)
		call.start(msecs / 1000)

