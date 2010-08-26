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
			return json.dumps({'response_type': 'Error',
				'code': 2,
				'description': 'Username and password not specified'})
		else:
			user = userAuth(email, password)
			if user:
				session['user_id'] = user.id
				return json.dumps({'response_type': 'Success',
					'user_id': user.id})
			else:
				return json.dumps({'response_type': 'Error',
					'code': 1,
					'description': 'Invalid credentials'})
			

def setup(jsonSite):
	userSite = JsonSite()
	userSite.putChild('login', UserLoginSite())
	jsonSite.putChild('user', userSite)


