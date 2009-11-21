import sbserver
from events import registerServerEventHandler, registerPolicyEventHandler
from colors import red
from xsbs.ui import error, insufficientPermissions
import xsbs.help
import logging
import sys, traceback

class UsageError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

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
		if self.command_handlers.has_key(command):
			for func in self.command_handlers[command]:
				try:
					func(cn, text)
				except UsageError as e:
					sbserver.playerMessage(cn, error('Usage: ' + repr(e)))
				except:
					exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
					logging.warn('Uncaught exception occured in command handler.')
					logging.warn(traceback.format_exc())
					logging.warn(traceback.extract_tb(exceptionTraceback))
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

registerCommandHandler('help', xsbs.help.onHelpCommand)
registerCommandHandler('listcommands', xsbs.help.listPublicCommands)

