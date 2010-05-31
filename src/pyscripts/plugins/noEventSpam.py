from xsbs.events import returnEventHandler, eventHandler
from xsbs.commands import commandHandler
from xsbs.players import masterRequired
import sbserver

EventHandler = returnEventHandler()

@commandHandler('liregevents')
@masterRequired
def onListRegEvents(p, args):
	'''@description List registered events
	   @usage
	   @admin'''
	for event in EventHandler.events.keys():
		#sbserver.message(event)
		@eventHandler(event)
		def onEvent(*args):
			sbserver.message(args)
