import sbserver
from events import registerServerEventHandler, registerPolicyEventHandler
from colors import red
from xsbs.ui import error, insufficientPermissions

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
				func(cn, text)
		else:
			sbserver.playerMessage(cn, error('Command not found'))
	def onMsg(self, cn, text):
		if self.prefixes.find(text[0]) != -1:
			cmd = text[1:].split(' ')[0]
			self.trigger(cn, cmd, text[len(cmd)+2:])
			return False
		return True

class masterRequired(object):
	def __init__(self, func):
		self.func = func
	def __call__(self, *args):
		if sbserver.playerPrivilege(args[0]) == 0:
			insufficientPermissions(args[0])
		else:
			self.func(*args)

class adminRequired(object):
	def __init__(self, func):
		self.func = func
	def __call__(self, *args):
		if sbserver.playerPrivilege(args[0]) <= 1:
			insufficientPermissions(args[0])
		else:
			self.func(*args)

commandmanager = CommandManager()

def registerCommandHandler(command, func):
	commandmanager.register(command, func)

def allowTeamSwitch(cn, team):
	sbserver.playerMessage(cn, 'You cannot switch to team %s' % team)
	return False

