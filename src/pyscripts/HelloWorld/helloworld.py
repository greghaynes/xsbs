import sbevents, sbserver

def talkteam(cn, text):
	print 'user ' + cn + ' said ' + text

def greet(cn):
	sbserver.message("Hello, " + sbserver.playerName(cn) + ".")
	print 'greeted'

def sayHello():
	print "Hello"

def init():
	sbevents.registerEventHandler("server_start", sayHello)
	sbevents.registerEventHandler("player_active", greet)
	sbevents.registerEventHandler("player_message_team", talkteam)
	
	return 0

init()