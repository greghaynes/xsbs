import sbserver, sbevents, sbtools

def showBanner():
	sbserver.message(sbtools.yellow('This is a ' + sbtools.blue('XSBS') + ' server.'))
	sbserver.message(sbtools.yellow('For information about ' + sbtools.blue('XSBS') + ' join ' + sbtools.orange('#xsbs') + ' on ' + sbtools.orange('irc.gamesurge.net') + '.'))
	sbevents.timerman.addTimer(18000, showBanner, ())

showBanner()

