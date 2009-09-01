import sbevents, sbserver
import string

template = string.Template("$name: $frags frags $deaths deaths $teamkills teamkills ($shots shots / $hits hits) $accuracy% accuracy")

def onCommand(cn, command):
	sp = command.split(' ')
	if len(sp) > 2:
		sbserver.playerMessage(cn, "Usage: #stats <cn>")
		return
	if len(sp) == 2:
		cn = int(sp[1])
	if sp[0] == 'stats':
		name = sbserver.playerName(cn)
		frags = sbserver.playerFrags(cn)
		deaths = sbserver.playerDeaths(cn)
		teamkills = sbserver.playerTeamkills(cn)
		shots = sbserver.playerShots(cn)
		hits = sbserver.playerHits(cn)
		accuracy = 0
		if shots != 0:
			accuracy = hits / float(shots)
			accuracy = accuracy * 100
		msg = template.substitute(name=name, frags=frags, deaths=deaths, teamkills=teamkills, shots=shots, hits=hits, accuracy=accuracy)
		sbserver.playerMessage(cn, msg)

sbevents.registerEventHandler('player_command', onCommand)

