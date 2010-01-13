from xsbs.http import urlHandler, regexUrlHandler, isMaster
from xsbs.http.json import jsonMasterRequired
from xsbs.players import all as allClients, player, playerCount, spectatorCount
from xsbs.net import ipLongToString
from xsbs.ban import ban
import sbserver
import json

@urlHandler('/json/login')
@jsonMasterRequired
def login(request):
	request.respond_with(200, 'text/plain', 0, json.dumps({
		'result': 'SUCCESS' }))

@urlHandler('/json/admin/ban_client')
@jsonMasterRequired
def banClient(request):
	try:
		cn = request.body['cn'][0]
		cn = int(cn)
	except (KeyError, IndexError):
		request.respond_with(200, 'text/plain', 0, json.dumps({
			'error': 'INVALID_PARAMS' }))
	try:
		secs = request.body['seconds'][0]
	except (KeyError, IndexError):
		secs = 1450
	secs = int(secs)
	try:
		reason = request.body['reason'][0]
	except (KeyError, IndexError):
		reason = 'Unspecified'
	request.respond_with(200, 'text/plain', 0, json.dumps({
		'result': 'SUCCESS' }))
	ban(cn, seconds, reason, -1)

@urlHandler('/json/admin/set_map')
@jsonMasterRequired
def setMap(request):
	try:
		map = request.body['map'][0]
		mode = request.body['mode'][0]
		mode = int(mode)
	except (KeyError, IndexError):
		request.respond_with(200, 'text/plain', 0, json.dumps({
			'error': 'INVALID_PARAMS' }))
	else:
		request.respond_with(200, 'text/plain', 0, json.dumps({
			'result': 'SUCCESS' }))
		sbserver.setMap(map, mode)

@urlHandler('/json/game')
def game(request):
	request.respond_with(200, 'text/plain', 0, json.dumps({
		'map': sbserver.mapName(),
		'mode': sbserver.gameMode(),
		'players': playerCount(),
		'spectators': spectatorCount() }))

@urlHandler('/json/server')
def server(request):
	request.respond_with(200, 'text/plain', 0, json.dumps({
		'num_clients': sbserver.numClients(),
		'master_mode': sbserver.masterMode(),
		'uptime': sbserver.uptime() }))

@urlHandler('/json/scoreboard')
def scoreboard(request):
	response = []
	for p in allClients():
		response.append( {
			'name': p.name(),
			'team': p.team(),
			'frags': p.frags(),
			'deaths': p.deaths(),
			'teamkills': p.teamkills(),
			'privilege': p.privilege(),
			})
	request.respond_with(200, 'text/plain', 0, json.dumps(response))

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
			'teamkills': p.teamkills(),
			'privilege': p.privilege()
			}
	request.respond_with(200, 'text/plain', 0, json.dumps(response))

@urlHandler('/json/clients')
def getClients(request):
	response = []
	for p in allClients():
		response.append( {
			'cn': p.cn,
			'name': p.name(),
			'team': p.team() 
			})
	request.respond_with(200, 'text/plain', 0, json.dumps(response))

