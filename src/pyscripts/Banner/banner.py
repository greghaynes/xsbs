import sbserver
from xsbs.settings import PluginConfig
from xsbs.timers import addTimer
from xsbs.colors import colordict
import string

class Banner:
	def __init__(self, message, delay):
		self.msg = string.Template(message).substitute(colordict)
		addTimer(delay, self.sendMessage, ())
	def sendMessage(self):
		sbserver.message(self.msg)
		addTimer(delay, self.sendMessage, ())

banners = []

config = PluginConfig('banner')
default_timeout = config.getOption('Config', 'default_timeout', 180000)
for option in config.getAllOptions('Banners'):
	msg = option[1]
	delay = config.getOption('Timeouts', option[0], default_timeout, False)
	banners.append(Banner(msg, int(delay)))
del config

