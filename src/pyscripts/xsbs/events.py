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

def registerServerEventHandler(event, func):
	server_events.connect(event, func)

def triggerServerEvent(event, args):
	server_events.trigger(event, args)

def registerPolicyEventHandler(event, func):
	policy_events.connect(event, func)

def triggerPolicyEvent(event, args):
	policy_events.trigger(event, args)

def update():
	timers.update()
	asyncore.loop(0)

