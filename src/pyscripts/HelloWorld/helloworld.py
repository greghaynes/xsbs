import sbevents, sbserver

def greet(cn):
	sbserver.message("Hello, " + sbserver.playerName(cn) + ".")

def init():
	sbevents.registerEventHandler("player_active", greet)
	return 0

init()
