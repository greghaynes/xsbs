import sbserver
from xsbs.events import registerServerEventHandler
from xsbs.commands import registerCommandHandler
from xsbs.colors import blue, red, orange

helptexts = {
	'help': (True,
		('#help <command>',),
		(
			'View information about a command',
			'Command arguments enclosed in <brackets> are required.',
			'Command arguments enclosed in (parenthesis) are optional.'
		)),
	'stats': (True,
		('#stats (cn)','#stats (name)'),
		('Display current game statistics of a player (or self).',)
		),
	'givemaster': (False,
		('#givemaster <cn>', '#givemaster <name>'),
		('Give master to a player.  You must be master or admin to use this command.',)
		),
	'giveadmin': (False,
		('#giveadmin <cn>', '#giveadmin <name>'),
		('Give admin to a player.  You must be admin to use this command.',)
		),
	'duel': (True,
		('#duel <mapname> (mode)',),
		('Begin a duel on specified map using specified game mode.',),
		),
        'translate': (True,
		('#translate <word>', '#translate <sentence/word> <from_lang> <to_lang>',),
		('Language codes: en, sv, de, it and lots more.',),
		)
}

### DO NOT MODIFY BELOW HERE ###
# UNLESS YOU HAVE SUPER POWERS #

available_commands_str = blue('Available commands: ')
available_commands_str += orange()
for command in helptexts.items():
	if command[1][0]:
		available_commands_str += '#' + command[0] + ' '

def onPlayerActive(cn):
	sbserver.playerMessage(cn, available_commands_str)

def msgHelpText(cn, cmd):
	try:
		helpinfo = helptexts[cmd]
	except KeyError:
		sbserver.playerMessage(cn, red('Command not found'))
	else:
		msgs = []
		for usage in helpinfo[1]:
			msgs.append(red(usage))
		for desc in helpinfo[2]:
			msgs.append(blue(desc))
		for msg in msgs:
			sbserver.playerMessage(cn, msg)

def onHelpCommand(cn, args):
	args = args.split(' ')
	if len(args) != 1:
		msgHelpText(cn, 'help')
	else:
		msgHelpText(cn, args[0])

def onPlayerCommands(cn, args):
	if args != '':
		sbserver.playerMessage(cn, red('Usage: #playercommands'))
	else:
		msg = blue('Available commands: ')
		for command in helptexts.keys():
			msg += '#' + command + ' '
		sbserver.playerMessage(cn, orange(msg))

registerServerEventHandler('player_connect_delayed', onPlayerActive)
registerCommandHandler('help', onHelpCommand)
registerCommandHandler('playercommands', onPlayerCommands)

