import sbevents, sbserver

def onPlayerSetMaster(cn, string):
	fooHash = sbserver.hashPassword(cn, 'foo')
	if string == fooHash:
		return True
	else:
		return False

sbevents.registerPolicyEventHandler('player_setmaster', onPlayerSetMaster)

