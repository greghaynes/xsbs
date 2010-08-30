from xsbs.events import eventHandler
from xsbs.players import isMaster
from xsbs.ui import insufficientPermissions, error
import sbserver

@eventHandler('player_request_spectate')
def onReqSpectate(cn, tcn):
	if tcn != cn:
		if isMaster(cn):
			sbserver.spectate(tcn)
		else:
			insufficientPermissions(cn)
	else:
		sbserver.spectate(tcn)

@eventHandler('player_request_unspectate')
def onReqUnspectate(cn, tcn):
	if tcn != cn:
		if isMaster(cn):
			sbserver.unspectate(tcn)
		else:
			insufficientPermissions(cn)
	else:
		if sbserver.masterMode() > 1 and not isAtLeastMaster(cn):
			sbserver.playerMessage(cn, error('Master mode is locked.  You cannot unspectate.'))
		else:
			sbserver.unspectate(tcn)

