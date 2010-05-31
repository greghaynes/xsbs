import sbserver
from xsbs.events import registerServerEventHandler
from xsbs.colors import blue, red, orange, colordict
from xsbs.ui import error, info
from xsbs.players import isMaster, isAdmin
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
		info.public = False
		info.master = False
		info.admin = False
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
					info.public = True
					valid = True
				elif tag == '@master':
					info.master = True
					valid = True
				elif tag == '@admin':
					info.admin = True
					valid = True
		if valid:
			command_info[command] = info
	else:
	     logging.warn('No help info for command: ' + command)

def msgHelpText(p, cmd):
	try:
		helpinfo = command_info[cmd]
	except KeyError:
		p.message(error('Command not found'))
	else:
		msgs = []
		try:
			msgs.append(helpinfo.description)
		except AttributeError:
			pass
		for usage in helpinfo.usages:
			msgs.append(usage)
		for msg in msgs:
			p.message(info(msg))

def onHelpCommand(p, args):
	'''@description Display help information about a command
	   @usage (command)
	   @public'''
	if args == '':
		msgHelpText(p, 'help')
	else:
		args = args.split(' ')
		msgHelpText(p, args[0])

def onPlayerCommands(p, args):
	if args != '':
		p.message(error('Usage: #playercommands'))
	else:
		msg = blue('Available commands: ')
		for command in command_info.keys():
			msg += '#' + command + ' '
		p.message(orange(msg))

def listCommands(p, args):
	'''@description Display all commands available to a user
	   @usage
	   @public'''
	if p.isAdmin():
		listAdminCommands(p, args)
	elif p.isMaster():
		listMasterCommands(p, args)
	else:
		listPublicCommands(p, args)
		
def listPublicCommands(p, args):
	str = 'Public commands: '
	for cmd in command_info.items():
		if cmd[1].public:
			str += cmd[1].command + ' '
	p.message(info(str))
	
def listMasterCommands(p, args):
	str = 'Master commands: '
	for cmd in command_info.items():
		if cmd[1].public:
			str += cmd[1].command + ' '
		elif cmd[1].master:
			str += cmd[1].command + ' '
	p.message(info(str))
	
def listAdminCommands(p, args):
	str = 'Admin commands: '
	for cmd in command_info.items():
		str += cmd[1].command + ' '
	p.message(info(str))
	
