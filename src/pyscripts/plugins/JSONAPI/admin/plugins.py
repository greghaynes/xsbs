from xsbs.http.jsonapi import JsonAdminSite

try:
	import json
except ImportError:
	import simplejson as json

class PluginSummarySite(JsonAdminSite):
	def __init__(self):
		JsonAdminSite.__init__(self)
	def render_admin_JSON(self, request):
		return json.dumps({
			

