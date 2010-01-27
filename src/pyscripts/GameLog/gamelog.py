from xsbs.events import registerServerEventHandler
from xsbs.players import player

import logging

event_handlers = (
	('player_connect', lambda x: logging.info(
		'connect: %s (%i)' % (player(x).name(), x))
		),
	('player_disconnect', lambda x: logging.info(
		'disconnect: %s (%i)' % (player(x).name(), x))
		),
	('player_message', lambda x, y: logging.info(
		'message: %s: %s' % (player(x).name(), y))
		),
	('player_message_team', lambda x, y: logging.info(
		'message (team): %s: %s' % (player(x).name(), y))
		)
	)

for ev_h in event_handlers:
	registerServerEventHandler(ev_h[0], ev_h[1])

