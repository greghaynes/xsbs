events = {}

def registerEventHandler(event, handler):
	if not events.has_key(event):
		events[event] = []
	events[event].append(handler)

def triggerEvent(event, args):
	if events.has_key(event):
		for handler in events[event]:
			handler(*args)