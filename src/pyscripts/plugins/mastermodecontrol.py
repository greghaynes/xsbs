from xsbs.events import eventHandler
from xsbs.ui import error, info
from xsbs.colors import green, blue
from xsbs.players import masterRequired
import sbserver
import string
config = {
	'Main':
		{
            '0':'open',
	        '1':'veto',
	        '2':'locked',
	        '3':'private'
		},
	'Templates':
		{
			'mm_set': '${client_name}${name}${text} set master mode to ${priv_master}${mm}',
		}
	}
def init():
    config['Templates']['mm_set'] = string.Template(config['Templates']['mm_set'])

init()

@eventHandler('player_set_mastermode')
@masterRequired
def setMM(cn, mm):
	sbserver.message(info(config['Templates']['mm_set'].substitute(themedict, name=sbserver.playerName(cn), mm = config['Main'][mm])))
	sbserver.setMasterMode(mm)

@eventHandler('no_clients')
def onNoClients():
	if sbserver.masterMode() > 1:
		sbserver.setMasterMode(1)
