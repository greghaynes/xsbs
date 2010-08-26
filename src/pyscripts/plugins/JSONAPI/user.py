from xsbs.http import server
from xsbs.http.jsonapi import site as apiSite, JsonSite, JsonSessionSite
from xsbs.users import userAuth

import json

class UserLoginSite(JsonSessionSite):
	def render_session_JSON(self, request, session):
		try:
			email = request.args['email']
			password = request.args['password']
		except (KeyError, IndexError):
			return 'error'
		else:
			user = userAuth(email, password)
			if user:
				session['user_id'] = user.id
				return 'success'
			else:
				return 'invalid username/password'
			

def setup(jsonSite):
	userSite = JsonSite()
	userSite.putChild('login', UserLoginSite())
	jsonSite.putChild('user', userSite)


