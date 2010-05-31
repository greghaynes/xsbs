from xsbs.events import returnEventHandler
from xsbs.commands import commandHandler
from xsbs.players import masterRequired
import sbserver
import dis

EventHandler = returnEventHandler()
EventHandler.events

@commandHandler('liregevents')
@masterRequired
def onListRegEvents(p, args):
	'''@description List registered events
	   @usage
	   @admin'''
	for event in EventHandler.events.keys():
		sbserver.message(event)
		for function in EventHandler.events[event]:
			sbserver.message(dis.dis(function))
