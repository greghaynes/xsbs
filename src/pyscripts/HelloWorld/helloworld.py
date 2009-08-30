import events

def sayHello():
	print "Hello"

def init():
	events.registerEventHandler("server_start", sayHello)
	return 0

init();