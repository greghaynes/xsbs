import sbserver
from xsbs.commands import registerCommandHandler
from xsbs.settings import PluginConfig
from xsbs.colors import green, white
import urllib2

cmd_name = 'mytime'
config = PluginConfig(cmd_name)
timezone = config.getOption('Config', 'timezone', 'EST')

def onCommand(cn, command):
     for i in urllib2.urlopen('http://tycho.usno.navy.mil/cgi-bin/timer.pl'):
          if 'EST' in i:
               sbserver.playerMessage(cn, green('The Eastern Standard Time is: ') + white(i))

registerCommandHandler(cmd_name, onCommand)

