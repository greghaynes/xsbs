from xsbs.http import urlHandler
from xsbs.players import all as allClients
import json

@urlHandler('/json/clients')
def getClients(request):
	response = []
	for player in allClients():
		response.append( {
			'cn': player.cn,
			'name': player.name(),
			'team': player.team() } )
	request.respond_with(200, 'text/html', 0, json.dumps(response))

