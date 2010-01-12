from xsbs.http import urlHandler, regexUrlHandler, isMaster
import json

class jsonMasterRequired(object):
	def __init__(self, func):
		self.func = func
		self.__doc__ = func.__doc__
		self.__name__ = func.__name__
	def __call__(self, *args, **kwargs):
		try:
			username = args[0].body['username'][0]
			password = args[0].body['password'][0]
			ismaster = isMaster(username, password)
		except (AttributeError, KeyError):
			args[0].respond_with(200, 'text/plain', 0, json.dumps(
				{ 'error': 'INVALID_LOGIN' }))
		else:
			if ismaster:
				self.func(*args, **kwargs)
			else:
				args[0].respond_with(200, 'text/plain', 0, json.dumps(
					{ 'error': 'INVALID_LOGIN' }))

