from xsbs.http.jsonapi import site as jsonSite, JsonAtLeastMasterSite, response
from xsbs.players import player
from xsbs.game import modeNumber

from JSONAPI.admin.server import setup as setupServerSite
from JSONAPI.admin.clients import setup as setupClientsSite

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
	setupServerSite(adminSite)
	setupClientsSite(adminSite)
	jsonSite.putChild('admin', adminSite)

