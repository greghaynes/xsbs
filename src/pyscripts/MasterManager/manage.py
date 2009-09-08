import sbevents, sbserver

master_pass = 'x5b5m45t3r'

def onPlayerSetMaster(cn, string):
	hash = sbserver.hashPassword(cn, master_pass)
	if string == hash:
		return True
	else:
		return False

sbevents.registerPolicyEventHandler('player_setmaster', onPlayerSetMaster)

