import sbevents, sbserver, sbtools
import string, math

template = string.Template(sbtools.green("$name: ") + sbtools.red("$frags") + sbtools.blue(" frags ") + sbtools.red("$deaths") + sbtools.blue(" deaths ") + sbtools.red("$teamkills") + sbtools.blue(" teamkills (") + sbtools.red("$shots") + sbtools.blue(" shots / ") + sbtools.red("$hits") + sbtools.blue(" hits) ") + sbtools.red("$accuracy") + sbtools.blue("% accuracy"))

def onCommand(cn, command):
	tcn = cn
	name = sbserver.playerName(tcn)
	frags = sbserver.playerFrags(tcn)
	deaths = sbserver.playerDeaths(tcn)
	teamkills = sbserver.playerTeamkills(tcn)
	shots = sbserver.playerShots(tcn)
	hits = sbserver.playerHits(tcn)
	accuracy = 0
	if shots != 0:
		accuracy = hits / float(shots)
		accuracy = math.trunc(accuracy * 100)
	msg = template.substitute(name=name, frags=frags, deaths=deaths, teamkills=teamkills, shots=shots, hits=hits, accuracy=accuracy)
	sbserver.playerMessage(cn, msg)

sbevents.registerCommandHandler('stats', onCommand)

