import events, sbserver

def greet(cn):
	sbserver.message("Hello, user")
	print 'greeted'

def sayHello():
	print "Hello"

def init():
	events.registerEventHandler("server_start", sayHello)
	events.registerEventHandler("player_active", greet)
	return 0

init()