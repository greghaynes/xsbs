import timers
import asyncore

class EventManager:
	def __init__(self):
		self.events = {}
	def connect(self, event, func):
		try:
			self.events[event].append(func)
		except KeyError:
			self.events[event] = []
			self.connect(event, func)
	def trigger(self, eventname, args=()):
		try:
			for event in self.events[eventname]:
				event(*args)
		except KeyError:
			pass

class PolicyEventManager(EventManager):
	def __init__(self):
		EventManager.__init__(self)
	def trigger(self, event, args=()):
		try:
			for event in self.events[event]:
				if not event(*args):
					return False
		except KeyError:
			return True
		return True

server_events = EventManager()
policy_events = PolicyEventManager()
exec_queue = []

def registerServerEventHandler(event, func):
	server_events.connect(event, func)

def triggerServerEvent(event, args):
	server_events.trigger(event, args)

def registerPolicyEventHandler(event, func):
	policy_events.connect(event, func)

def triggerPolicyEvent(event, args):
	return policy_events.trigger(event, args)

def execLater(func, args):
	exec_queue.append((func, args))

def triggerExecQueue():
	for event in exec_queue:
		try:
			event[0](*event[1])
		except:
			print 'Error executing execLater op.'
	del exec_queue[:]

def update():
	timers.update()
	asyncore.loop(0, False, None, count=1)
	triggerExecQueue()

