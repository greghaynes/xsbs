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
		if len(text) > 0 and self.prefixes.find(text[0]) != -1:
			cmd = text[1:].split(' ')[0]
			self.trigger(cn, cmd, text[len(cmd)+2:])
			return False
		return True

commandmanager = CommandManager()

def registerCommandHandler(command, func):
	commandmanager.register(command, func)

def allowTeamSwitch(cn, team):
	sbserver.playerMessage(cn, 'You cannot switch to team %s' % team)
	return False

