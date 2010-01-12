import sbserver
from xsbs.colors import red, green
from xsbs.settings import PluginConfig
from xsbs.commands import registerCommandHandler

cmd_name = 'sauerhelp'

config = PluginConfig('sauerhelp')
command = config.getOption('Config', 'command', 'newmap')
del config

commands = dict(newmap="Creates a blank map, arguments for this command are '/newmap size' where size is a number 10-16",
                sendmap="/sendmap uploads your map to the server so other players are able to see it this command has no arguments",
                getmap="downloads the map that has been uploaded to the server by another user, this command has no arguments",
                savemap="saves the map for later access, arguments for this command are '/savemap mapname'",
                calclight="calculates lightmaps for all light entities on the map use '/calclight -1' which calculates the lights faster",
                lightprecision="changes the precision of the shadows when you calclight, arguments for this command are '/lightprecision number' where number is the detail level",
                kill="causes player to commit suicide and takes away 1 point, there are no arguments for this command")

		
def onCommand(cn, command):
			sbserver.playerMessage(cn, green(command) + green(": ") + red(commands[command]))                    
			

registerCommandHandler(cmd_name, onCommand)
