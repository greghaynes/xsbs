import sbserver
from xsbs.events import registerServerEventHandler
from xsbs.colors import blue, red, orange, colordict
from xsbs.ui import error, info
from xsbs.settings import PluginConfig
import logging

class CommandInfo:
	def __init__(self, command):
		self.command = command
		self.usages = []
		self.public = False
	def addUsage(self, str):
	 	str = '#' + self.command + ' ' + str
		self.usages.append(str)

command_info = {}

def loadCommandInfo(command, handler):
	docs = handler.__doc__
	if docs != None:
		info = CommandInfo(command)
		lines = docs.split('\n')
		valid = False
		for line in lines:
			line = line.strip()
			if line[0] == '@':
				tag = line.split(' ', 1)[0]
				if tag == '@usage':
					if len(line) == len(tag):
						info.addUsage('')
					else:
						info.addUsage(line[len(tag)+1:])
					valid = True
				elif tag == '@description':
					info.description = line[len(tag)+1:]
					valid  = True
				elif tag == '@public':
					info.public == True
					valid = True
		if valid:
			command_info[command] = info
	else:
	     logging.warn('No help info for command: ' + command)

def msgHelpText(cn, cmd):
	try:
		helpinfo = command_info[cmd]
	except KeyError:
		sbserver.playerMessage(cn, error('Command not found'))
	else:
		msgs = []
		try:
			msgs.append(helpinfo.description)
		except AttributeError:
			pass
		for usage in helpinfo.usages:
			msgs.append(usage)
		for msg in msgs:
			sbserver.playerMessage(cn, info(msg))

def onHelpCommand(cn, args):
	'''@description Display help information about a command
	   @usage
	   @usage (command)
	   @public'''
	if args == '':
		msgHelpText(cn, 'help')
	else:
		args = args.split(' ')
		msgHelpText(cn, args[0])

def onPlayerCommands(cn, args):
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #playercommands'))
	else:
		msg = blue('Available commands: ')
		for command in helptexts.keys():
			msg += '#' + command + ' '
		sbserver.playerMessage(cn, orange(msg))

