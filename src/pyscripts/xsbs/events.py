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
	def trigger(self, event, args=()):
		try:
			for event in self.events[event]:
				event(*args)
		except KeyError:
			pass

server_events = EventManager()
policy_events = EventManager()
postevent_handlers = []

def registerServerEventHandler(event, func):
	server_events.connect(event, func)

def triggerServerEvent(event, args):
	del postevent_handlers[:]
	server_events.trigger(event, args)
	triggerPostEventHandlers()

def registerPolicyEventHandler(event, func):
	policy_events.connect(event, func)

def triggerPolicyEvent(event, args):
	del postevent_handlers[:]
	policy_events.trigger(event, args)
	triggerPostEventHandlers()

def registerPostEventHandler(func, args):
	postevent_handlers.append((func, args))

def triggerPostEventHandlers():
	for event in postevent_handlers:
		event[0](event[1])

def update():
	timers.update()
	asyncore.loop(0, False, None, count=1)

