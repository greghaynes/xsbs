from xsbs.http.jsonapi import site as jsonSite, JsonAtLeastMasterSite, response
from xsbs.players import player
from xsbs.game import modeNumber

from config import setup as setupConfigSite

import sbserver

try:
	import json
except ImportError:
	import simplejson as json

class AdminSite(JsonAtLeastMasterSite):
	pass

def setup(jsonSite):
	'''Called by JSONAPI/api.py'''
	adminSite = AdminSite()
	setupConfigSite(adminSite)
	jsonSite.putChild('admin', adminSite)

