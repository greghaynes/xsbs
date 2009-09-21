import sbserver
from xsbs.colors import orange, yellow

def notice(message):
	sbserver.message(orange('Notice: ' + message))

def info(message):
	sbserver.message(yellow('Info: ' + message))

