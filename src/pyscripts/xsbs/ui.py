import sbserver
from xsbs.colors import colordict
from xsbs.settings import loadPluginConfig

import string
import logging

config = {
	'MessageTypes':
		{
			'notice': '${blue}Notice:${text}',
			'info': '${yellow}Info:${text}',
			'warning': '${red}Warning:${text}',
			'error': '${red}Error:${text}',
		},
	'Theme':
		{
			'priv_master': 'blue',
			'priv_admin': 'red',
			'client_name': 'green',
			'secondary_client_name': 'blue',
			'text': 'white',
			'severe_action': 'red',
			'emphasis': 'orange'
		}
	}

themedict = dict(**colordict)

def init():
	loadPluginConfig(config, 'UI')
	for name, colorname in config['Theme'].items():
		try:
			themedict[name] = colordict[colorname]
		except KeyError:
			logging.error('Invalid color \'%s\' specified for \'%s\'' % (colorname, name))

	for msgtype, theme in config['MessageTypes'].items():
		config['MessageTypes'][msgtype] = string.Template(config['MessageTypes'][msgtype]).substitute(themedict) + ' '

def notice(message):
	return config['MessageTypes']['notice'] + message

def info(message):
	return config['MessageTypes']['info'] + message

def warning(message):
	return config['MessageTypes']['warning'] + message

def error(message):
	return config['MessageTypes']['error'] + message

def insufficientPermissions(cn):
	sbserver.playerMessage(cn, error('Insufficient permissions'))
	
init()

