import sbserver, sbevents, sbtools, settings
from settings import PluginConfig
import string

banners = []

config = PluginConfig('banner')
default_timeout = config.getOption('Config', 'default_timeout', 180000)
for option in config.getAllOptions('Banners'):
	banner = option[1]
	delay = config.getOption('Timeouts', option[0], default_timeout, False)
	banners.append((banner, delay))
del config

def showBanner(msg, timeout):
	sbserver.message(msg)
	sbevents.timerman.addTimer(timeout, showBanner, (msg, timeout))

