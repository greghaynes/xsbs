from xsbs.events import registerServerEventHandler
from xsbs.ui import error, info
from xsbs.colors import green, blue
from xsbs.players import masterRequired
import sbserver

MMNAMES = ['open',
	'veto',
	'locked',
	'private']

@masterRequired
def setMM(cn, mm):
	sbserver.message((info(green('%s') + ' set master mode to ' + blue('%s')) % (sbserver.playerName(cn), MMNAMES[mm])))
	sbserver.setMasterMode(mm)

def onNoClients():
	if sbserver.masterMode() > 1:
		sbserver.setMasterMode(1)

registerServerEventHandler('player_set_mastermode', setMM)
registerServerEventHandler('no_clients', onNoClients)

