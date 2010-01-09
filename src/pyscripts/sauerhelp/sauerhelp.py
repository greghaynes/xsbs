import sbserver
from xsbs.colors import red, green
from xsbs.settings import PluginConfig
from xsbs.commands import registerCommandHandler

cmd_name = 'sauerhelp'

config = PluginConfig('sauerhelp')
command = config.getOption('Config', 'command', 'newmap')
del config

commands = dict(newmap="Creates a blank map, arguments for this command are '/newmap size' where size is a number 10-16",
                sendmap="/sendmap uploads your map to the server so other players are able to see it this command has no arguments")

		
def onCommand(cn, command, args=()):
			sbserver.playerMessage(cn, green(command) + green(": ") + red(commands[command]))                    
			

registerCommandHandler(cmd_name, onCommand)
