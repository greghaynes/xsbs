from xsbs.http import server
from xsbs.http.jsonapi import site as apiSite, JsonSite, JsonSessionSite, JsonUserSite
from xsbs.users import userAuth, User

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import json

class LoginSite(JsonSessionSite):
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
			
class ProfileSite(JsonSessionSite):
	def render_user_JSON(self, request, session, user_id):
		try:
			user = User.query.filter(id=user_id).one()
		except (NoResultFound, MultipleResultsFound):
			return json.dumps({'response_type': 'Error', 'code': '1'})
		return json.dumps({'response_type': 'Success',
			'id': user.id,
			'username': user.username})

def setup(jsonSite):
	userSite = JsonSite()
	userSite.putChild('login', LoginSite())
	jsonSite.putChild('user', userSite)


