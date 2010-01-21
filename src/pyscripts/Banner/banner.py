from xsbs.settings import PluginConfig
from xsbs.timers import addTimer
from xsbs.colors import colordict
from xsbs.ui import notice
from xsbs.server import message
import string

class Banner:
	def __init__(self, msg, delay):
		self.msg = string.Template(msg).substitute(colordict)
		self.delay = delay
		addTimer(delay, self.sendMessage, ())
	def sendMessage(self):
		message(notice(self.msg))
		addTimer(self.delay, self.sendMessage, ())

banners = []

def setup():
	config = PluginConfig('banner')
	default_timeout = config.getOption('Config', 'default_timeout', 180000)
	for option in config.getAllOptions('Banners'):
		msg = option[1]
		delay = config.getOption('Timeouts', option[0], default_timeout, False)
		banners.append(Banner(msg, int(delay)))
	del config

setup()

