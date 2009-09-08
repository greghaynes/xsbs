import sbevents, sbserver, sbtools

master_pass = 'x5b5m45t3r'

def onPlayerSetMaster(cn, string):
	hash = sbserver.hashPassword(cn, master_pass)
	if string == hash:
		return True
	else:
		return False

def onGiveMaster(cn, string):
	tcn = int(string)
	if sbserver.playerPrivilege(cn) > 0:
		sbserver.setMaster(tcn)
	else:
		sbserver.playerMessage(cn, sbtools.red('Insufficient privileges.'))

def onGiveAdmin(cn, string):
	tcn = int(string)
	if sbserver.playerPrivilege(cn) > 1:
		sbserver.setAdmin(tcn)
	else:
		sbserver.playerMessage(cn, sbtools.red('Insufficient privileges.'))

sbevents.registerPolicyEventHandler('player_setmaster', onPlayerSetMaster)
sbevents.registerCommandHandler('givemaster', onGiveMaster)
sbevents.registerCommandHandler('giveadmin', onGiveAdmin)

