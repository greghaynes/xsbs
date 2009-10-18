from xsbs.events import registerServerEventHandler
from UserPrivelege.userpriv import isPlayerMaster
from xsbs.ui import insufficientPermissions, error
import sbserver

def onReqSpectate(cn, tcn):
	if tcn != cn:
		if isPlayerMaster(cn) or sbserver.playerPrivilege(cn) > 0:
			sbserver.spectate(tcn)
		else:
			insufficientPermissions(cn)
	else:
		sbserver.spectate(tcn)

def onReqUnspectate(cn, tcn):
	if tcn != cn:
		if isPlayerMaster(cn) or sbserver.playerPrivilege(cn) > 0:
			sbserver.unspectate(tcn)
		else:
			insufficientPermissions(cn)
	else:
		if sbserver.masterMode() > 1 and not (isPlayerMaster(cn) or sbserver.playerPrivilege(cn) > 0):
			sbserver.playerMessage(cn, error('Master mode is locked.  You cannot unspectate.'))
		else:
			sbserver.unspectate(tcn)

registerServerEventHandler('player_request_spectate', onReqSpectate)
registerServerEventHandler('player_request_unspectate', onReqUnspectate)

