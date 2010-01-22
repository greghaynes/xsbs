import sbserver
from events import registerServerEventHandler, registerPolicyEventHandler
from colors import red
from xsbs.ui import error, info, insufficientPermissions
from xsbs.players import playerByName, player
from xsbs.help import command_info
import xsbs.help
import logging
import sys, traceback

class UsageError(Exception):
	'''Invalid client usage of command'''
	def __init__(self, value=''):
		Exception.__init__(self, value)

class ExtraArgumentError(UsageError):
	'''Argument specified when none expected'''
	def __init__(self):
		UsageError.__init__(self, 'Extra argument specified')

class StateError(Exception):
	'''State of server is invalid for command'''
	def __init__(self, value):
		Exception.__init__(self, value)

class ArgumentValueError(Exception):
	'''Value of an argument is erroneous'''
	def __init__(self, value):
		Exception.__init__(self, value)

class CommandManager:
	def __init__(self):
		self.prefixes = '#!@'
		self.command_handlers = {}
		registerPolicyEventHandler('allow_message', self.onMsg)
	def register(self, command, func):
		if not self.command_handlers.has_key(command):
			self.command_handlers[command] = []
		self.command_handlers[command].append(func)
	def trigger(self, cn, command, text):
		p = player(cn)
		if self.command_handlers.has_key(command):
			for func in self.command_handlers[command]:
				try:
					func(cn, text)
				except UsageError as e:
					try:
						usages = command_info[command].usages
					except KeyError:
						usages = []
					p.message(error('Invalid Usage of #' + command + ' command. ' + str(e)))
					for usage in usages:
						p.message(info('Usage: ' + command + ' ' + usage))
				except StateError as e:
					p.message(error(str(e)))
				except ArgumentValueError as e:
					p.message(error('Invalid argument. ' + str(e)))
				except ValueError:
					p.message(error('Value Error: Did you specify a valid cn?'))
					exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
					logging.warn('Uncaught ValueError raised in command handler.')
					logging.warn(traceback.format_exc())
				except:
					exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
					logging.warn('Uncaught exception occured in command handler.')
					logging.warn(traceback.format_exc())
		else:
			sbserver.playerMessage(cn, error('Command not found'))
	def onMsg(self, cn, text):
		if len(text) > 0 and self.prefixes.find(text[0]) != -1:
			cmd = text[1:].split(' ')[0]
			self.trigger(cn, cmd, text[len(cmd)+2:])
			return False
		return True

commandmanager = CommandManager()

def registerCommandHandler(command, func):
	xsbs.help.loadCommandInfo(command, func)
	commandmanager.register(command, func)

class commandHandler(object):
	def __init__(self, name):
		self.command_name = name
	def __call__(self, f):
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		registerCommandHandler(self.command_name, f)
		return f

class cnArg(object):
	def __init__(self, argnum=0):
		self.argnum = argnum
	def __call__(self, f):
		self.func = f
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		return self.handle
	def handle(self, cn, args):
		arg = args[self.argnum]
		try:
			cn = int(arg)
		except TypeError:
			cn = playerByName(arg).crn
		args[self.argnum] = cn
		return self.func(cn, args)

registerCommandHandler('help', xsbs.help.onHelpCommand)
registerCommandHandler('listcommands', xsbs.help.listPublicCommands)

