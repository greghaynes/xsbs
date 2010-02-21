from xsbs.events import eventHandler
from xsbs.ui import error, info
from xsbs.colors import green, blue
from xsbs.players import masterRequired
import sbserver

MMNAMES = ['open',
	'veto',
	'locked',
	'private']

@eventHandler('player_set_mastermode')
@masterRequired
def setMM(cn, mm):
	sbserver.message((info(green('%s') + ' set master mode to ' + blue('%s')) % (sbserver.playerName(cn), MMNAMES[mm])))
	sbserver.setMasterMode(mm)

@eventHandler('no_clients')
def onNoClients():
	if sbserver.masterMode() > 1:
		sbserver.setMasterMode(1)