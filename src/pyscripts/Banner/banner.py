import sbserver, sbevents, sbtools
from ConfigParser import ConfigParser
import string

banners = []
timeout = 180000

def showBanner():
	for banner in banners:
		sbserver.message(banner)
	sbevents.timerman.addTimer(timeout, showBanner, ())

conf = ConfigParser()
conf.read('Banner/plugin.conf')
for template in conf.options('Templates'):
	banners.append(string.Template(conf.get('Templates', template)).substitute(sbtools.colordict))
if conf.has_option('Banner', 'delay'):
	timeout = int(conf.get('Banner', 'delay'))
del conf

showBanner()

