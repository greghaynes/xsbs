import sbserver
from xsbs.colors import colordict
from xsbs.settings import loadPluginConfig
import string

config = {
	'Templates':
		{
			'notice': '${blue}Notice:${white}',
			'info': '${yellow}Info:${white}',
			'warning': '${red}Warning:${white}',
			'error': '${red}Error:${white}',
		}
	}

def init():
	loadPluginConfig(config, 'UI')
	config['Templates']['notice'] = 	string.Template(config['Templates']['notice'])
	config['Templates']['info'] = 		string.Template(config['Templates']['info'])
	config['Templates']['warning'] = 	string.Template(config['Templates']['warning'])
	config['Templates']['error'] = 		string.Template(config['Templates']['error'])


	config['Templates']['notice'] = 	config['Templates']['notice'].substitute(colordict) + ' '
	config['Templates']['info'] = 		config['Templates']['info'].substitute(colordict) + ' '
	config['Templates']['warning'] = 	config['Templates']['warning'].substitute(colordict) + ' '
	config['Templates']['error'] = 		config['Templates']['error'].substitute(colordict) + ' '

def notice(message):
	return config['Templates']['notice'] + message

def info(message):
	return config['Templates']['info'] + message

def warning(message):
	return config['Templates']['warning'] + message

def error(message):
	return config['Templates']['error'] + message

def insufficientPermissions(cn):
	sbserver.playerMessage(cn, error('Insufficient permissions'))
	
init()

