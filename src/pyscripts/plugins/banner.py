from xsbs.settings import loadPluginConfig
from xsbs.timers import addTimer
from xsbs.colors import colordict
from xsbs.ui import notice
from xsbs.server import message
import string

class Banner(object):
	def __init__(self, msg, delay):
		self.msg = string.Template(msg).substitute(colordict)
		self.delay = delay
		addTimer(delay, self.sendMessage, ())
	def sendMessage(self):
		message(notice(self.msg))
		addTimer(self.delay, self.sendMessage, ())

banners = []

def setup():
	config = {
		'Main': {
			'default_frequency': 180000,
			},
		'Banners': {},
		'Timeouts': {},
		}
	loadPluginConfig(config, 'Banners')
	default_timeout = config['Main']['default_frequency']
	for key, value in config['Banners'].items():
		msg = value
		try:
			delay = config['Timeouts'][key]
		except KeyError:
			delay = default_timeout
		banners.append(Banner(msg, int(delay)))
	del config

setup()

