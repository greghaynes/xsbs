import sbserver
from xsbs.colors import colordict
from xsbs.settings import PluginConfig
import string

config = PluginConfig('ui')
notice_pre = config.getOption('Prefixes', 'notice', '${blue}Notice:')
info_pre = config.getOption('Prefixes', 'info', '${yellow}Info:')
warning_pre = config.getOption('Prefixes', 'warning', '${red}Warning:')
error_pre = config.getOption('Prefixes', 'error', '${red}Error:')
del config

notice_pre = string.Template(notice_pre).substitute(colordict) + ' '
info_pre = string.Template(info_pre).substitute(colordict) + ' '
warning_pre = string.Template(warning_pre).substitute(colordict) + ' '
error_pre = string.Template(error_pre).substitute(colordict) + ' '

def notice(message):
	return notice_pre + message

def info(message):
	return info_pre + message

def warning(message):
	return warning_pre + message

def error(message):
	return error_pre + message

def insufficientPermissions(cn):
	sbserver.playerMessage(cn, error('Insufficient permissions'))

