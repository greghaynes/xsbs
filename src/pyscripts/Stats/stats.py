import sbevents, sbserver
import string

template = string.Template("$name: $frags frags $deaths deaths $teamkills teamkills ($shots shots / $hits hits) $accuracy% accuracy")

def onCommand(cn, command):
	sp = command.split(' ')
	tcn = cn
	if len(sp) > 2:
		sbserver.playerMessage(cn, "Usage: #stats <cn>")
		return
	if len(sp) == 2:
		tcn = int(sp[1])
	if sp[0] == 'stats':
		name = sbserver.playerName(tcn)
		frags = sbserver.playerFrags(tcn)
		deaths = sbserver.playerDeaths(tcn)
		teamkills = sbserver.playerTeamkills(tcn)
		shots = sbserver.playerShots(tcn)
		hits = sbserver.playerHits(tcn)
		accuracy = 0
		if shots != 0:
			accuracy = hits / float(shots)
			accuracy = accuracy * 100
		msg = template.substitute(name=name, frags=frags, deaths=deaths, teamkills=teamkills, shots=shots, hits=hits, accuracy=accuracy)
		sbserver.playerMessage(cn, msg)

sbevents.registerEventHandler('player_command', onCommand)

