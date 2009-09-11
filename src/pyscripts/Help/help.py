import sbserver, sbevents, sbtools

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
}

### DO NOT MODIFY BELOW HERE ###
# UNLESS YOU HAVE SUPER POWERS #

available_commands_str = sbtools.blue('Available commands: ')
available_commands_str += sbtools.orange()
for command in helptexts.items():
	if command[1][0]:
		available_commands_str += '#' + command[0] + ' '

def onPlayerActive(cn):
	sbserver.playerMessage(cn, available_commands_str)

def msgHelpText(cn, cmd):
	try:
		helpinfo = helptexts[cmd]
	except KeyError:
		sbserver.playerMessage(cn, sbtools.red('Command not found'))
	else:
		msgs = []
		for usage in helpinfo[1]:
			msgs.append(sbtools.red(usage))
		for desc in helpinfo[2]:
			msgs.append(sbtools.blue(desc))
		for msg in msgs:
			sbserver.playerMessage(cn, msg)

def onHelpCommand(cn, args):
	args = args.split(' ')
	if len(args) != 1:
		msgHelpText(cn, 'help')
	else:
		msgHelpText(cn, args[0])

sbevents.registerEventHandler('player_active', onPlayerActive)
sbevents.registerCommandHandler('help', onHelpCommand)

