import sbserver
from xsbs.colors import blue

def notice(message):
	sbserver.message(blue('Notice: ' + message))

