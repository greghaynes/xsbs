from xsbs.http import server
from xsbs.http.jsonapi import site as apiSite, JsonSite, JsonSessionSite

import json

class CreateSessionSite(JsonSessionSite):
	def render_session_JSON(self, request, session):
		session = server.session_manager.createSession()
		return json.dumps({'key': session.key})

def setup(jsonSite):
	sessionSite = JsonSite()
	sessionSite.putChild('create', CreateSessionSite())
	jsonSite.putChild('session', sessionSite)

