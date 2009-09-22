import sbserver
from xsbs.colors import orange, yellow, red, blue

def notice(message):
	return blue('Notice: ') + message

def info(message):
	return yellow('Info: ') + message

def warning(message):
	return red('Warning: ') + message

def error(message):
	return red('Error: ') + message

def insufficientPermissions(cn):
	sbserver.playerMessage(cn, error('Insufficient permissions'))

