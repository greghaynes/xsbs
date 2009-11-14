import timers
import asyncore
import logging
import sys
import traceback

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
				try:
					event(*args)
				except:
					exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
					logging.warn('Uncaught exception occured in event handler.')
					logging.warn(traceback.format_exc())
					logging.warn(traceback.extract_tb(exceptionTraceback))
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

class eventHandler(object):
	def __init__(self, name):
		self.name = name
	def __call__(self, f):
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		registerServerEventHandler(self.name, f)
		return f

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
			exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
			logging.warn('Uncaught exception execLater queue.')
			logging.warn(traceback.format_exc())
			logging.warn(traceback.extract_tb(exceptionTraceback))
	del exec_queue[:]

def update():
	timers.update()
	asyncore.loop(0, False, None, count=1)
	triggerExecQueue()

