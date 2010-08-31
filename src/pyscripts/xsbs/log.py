from xsbs.settings import PluginConfig
import sbserver
import logging
import string

path = sbserver.logPath()
level = sbserver.logLevel()

LEVELS = {'debug': logging.DEBUG,
	'info': logging.INFO,
	'warning': logging.WARNING,
	'error': logging.ERROR,
	'critical': logging.CRITICAL}

logging.basicConfig(
	filename = path,
	format = '%(levelname)-10s %(asctime)s %(module)s: %(message)s',
	level = LEVELS[level])

