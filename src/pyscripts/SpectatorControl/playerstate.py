from xsbs.events import registerServerEventHandler
from xsbs.players import isAtLeastMaster
from xsbs.ui import insufficientPermissions, error
import sbserver

def onReqSpectate(cn, tcn):
	if tcn != cn:
		if isAtLeastMaster(cn):
			sbserver.spectate(tcn)
		else:
			insufficientPermissions(cn)
	else:
		sbserver.spectate(tcn)

def onReqUnspectate(cn, tcn):
	if tcn != cn:
		if isAtLeastMaster(cn):
			sbserver.unspectate(tcn)
		else:
			insufficientPermissions(cn)
	else:
		if sbserver.masterMode() > 1 and not isAtLeastMaster(cn):
			sbserver.playerMessage(cn, error('Master mode is locked.  You cannot unspectate.'))
		else:
			sbserver.unspectate(tcn)

registerServerEventHandler('player_request_spectate', onReqSpectate)
registerServerEventHandler('player_request_unspectate', onReqUnspectate)

