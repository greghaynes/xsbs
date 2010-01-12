from xsbs.http import urlHandler, regexUrlHandler
from xsbs.players import all as allClients, player
import json

@regexUrlHandler('/json/clients/(?P<cn>\d+)')
def clientDetail(request, cn):
	try:
		p = player(int(cn))
	except ValueError:
		response = { 'error': 'Invalid cn' }
	else:
		response = { 'cn': p.cn,
			'name': p.name(),
			'team': p.team(),
			'frags': p.frags(),
			'deaths': p.deaths(),
			'teamkills': p.teamkills() }
	request.respond_with(200, 'text/html', 0, json.dumps(response))

@urlHandler('/json/clients')
def getClients(request):
	response = []
	for player in allClients():
		response.append( {
			'cn': player.cn,
			'name': player.name(),
			'team': player.team() } )
	request.respond_with(200, 'text/html', 0, json.dumps(response))

