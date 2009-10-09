from xsbs.events import registerServerEventHandler
from xsbs.ui import error, info
import sbserver

MMNAMES = ['open',
	'veto',
	'locked',
	'private']

def setMM(cn, mm):
	if sbserver.playerPrivilege(cn) > 0:
		sbserver.message(info('%s set master mode to %s' % (sbserver.playerName(cn), MMNAMES[mm])))
		sbserver.setMasterMode(mm)
	else:
		sbserver.playerMessage(cn, error('You cannot set the master mode.'))

def onNoClients():
	if sbserver.masterMode() > 1:
		sbserver.setMasterMode(1)

registerServerEventHandler('player_set_mastermode', setMM)
registerServerEventHandler('no_clients', onNoClients)

