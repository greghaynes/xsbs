from xsbs.events import registerServerEventHandler, triggerServerEvent
import sbserver

def onIntermEnd():
	triggerServerEvent('reload_map_selection', ())
	sbserver.sendMapReload()

registerServerEventHandler('intermission_ended', onIntermEnd)

