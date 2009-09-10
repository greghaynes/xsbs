import sbserver, sbevents, sbtools, settings
from settings import loadConfigFile
from ConfigParser import ConfigParser
import string

banners = []
timeout = 180000

def showBanner(msg, timeout):
	sbserver.message(msg)
	sbevents.timerman.addTimer(timeout, showBanner, (msg, timeout))

conf = loadConfigFile('banner')
for template in conf.options('Templates'):
	delay = timeout
	if conf.has_option('Delays', template):
		delay = int(conf.get('Delays', template))
	banners.append((string.Template(conf.get('Templates', template)).substitute(sbtools.colordict), delay))
if conf.has_option('Banner', 'delay'):
	timeout = int(conf.get('Banner', 'delay'))
del conf

for banner in banners:
	showBanner(*banner)

