from xsbs.events import registerServerEventHandler
from UserPrivelege.userpriv import isPlayerMaster
from xsbs.ui import insufficientPermissions, error
import sbserver

def onReqSpectate(cn, tcn):
	if tcn != cn:
		if isPlayerMaster(cn) or sbserver.playerPrivilege(cn) > 0:
			sbserver.spectate(cn, tcn)
		else:
			insufficientPermissions(cn)
	else:
		sbserver.spectate(cn, tcn)

def onReqUnspectate(cn, tcn):
	if tcn != cn:
		if isPlayerMaster(cn) or sbserver.playerPrivilege(cn) > 0:
			sbserver.spectate(cn, tcn)
		else:
			insufficientPermissions(cn)
	else:
		if sbserver.masterMode() > 1 and not (isPlayerMaster(cn) or sbserver.playerPrivilege(cn) > 0):
			sbserver.playerMessage(cn, error('Master mode is locked.  You cannot unspectate.'))
		else:
			sbserver.unspectate(cn, tcn)

registerServerEventHandler('player_request_spectate', onReqSpectate)
registerServerEventHandler('player_request_unspectate', onReqUnspectate)

