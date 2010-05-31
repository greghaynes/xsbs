from xsbs.events import returnEventHandler
from xsbs.commands import commandHandler
from xsbs.players import masterRequired
import sbserver


EventHandler = returnEventHandler()
EventHandler.events

@commandHandler('liregevents')
@masterRequired
def onListRegEvents(p, args):
	'''@description List registered events
	   @usage
	   @admin'''
	for event in EventHandler.events.keys():
		for function in EventHandler.events[event]:
			sbserver.message(function)
