import timers
import asyncore
import logging
import sys
import traceback
import sbserver
from twisted.internet import reactor

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
					logging.error('Uncaught exception occured in event handler.')
					logging.error(traceback.format_exc())
		except KeyError:
			pass
	def trigger_cs(self, eventname, args=()):
		sbserver.triggercsevent(eventname, args)

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
	'''Call function when event has been executed.'''
	server_events.connect(event, func)

class eventHandler(object):
	'''Decorator which registers a function as an event handler.'''
	def __init__(self, name):
		self.name = name
	def __call__(self, f):
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		registerServerEventHandler(self.name, f)
		return f

def triggerServerEvent(event, args):
	'''Trigger event with arguments.'''
	server_events.trigger(event, args)
	server_events.trigger_cs(event, args)

def registerPolicyEventHandler(event, func):
	'''Call function when policy event has been executed.'''
	policy_events.connect(event, func)

class policyHandler(object):
	'''Decorator which registers a function as a policy event handler.'''
	def __init__(self, name):
		self.name = name
	def __call__(self, f):
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		registerPolicyEventHandler(self.name, f)
		return f

def triggerPolicyEvent(event, args):
	'''Trigger policy event with arguments.'''
	return policy_events.trigger(event, args)

def execLater(func, args):
	'''Call function at a later time with arguments in tuple args.'''
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

@eventHandler('reload')
def onReload():
	server_events.events.clear()

def update():
	reactor.runUntilCurrent()
	reactor.doIteration(0)
	triggerExecQueue()

reactor.startRunning()

