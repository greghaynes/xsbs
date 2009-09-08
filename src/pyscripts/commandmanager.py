import sbevents, sbserver, sbtools

class CommandManager:
	def __init__(self):
		self.prefixes = '#!@'
		self.command_handlers = {}
		sbevents.registerPolicyEventHandler('allow_message', self.onMsg)
	def register(self, command, func):
		if not self.command_handlers.has_key(command):
			self.command_handlers[command] = []
		self.command_handlers[command].append(func)
	def trigger(self, cn, command):
		if self.command_handlers.has_key(command):
			for func in self.command_handlers[command]:
				func(cn, str)
		else:
			sbserver.playerMessage(cn, sbtools.red('Command not found.'))
	def onMsg(self, cn, text):
		if self.prefixes.find(text[0]) != -1:
			cmd = text.split(' ')[0][1:]
			self.trigger(cn, text[len(cmd)+2:])
			return False
		return True

