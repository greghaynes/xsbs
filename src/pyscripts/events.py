events = {}

def register_event_handler(event, handler):
	if not events.has_key(event):
		events[event] = []
	events[event].append(handler)

def trigger_event(event, args):
	for handler in events[event]:
		handler(*args)