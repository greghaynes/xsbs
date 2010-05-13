from xsbs.http.jsonapi import JsonAdminSite
from xsbs.settings import pluginNames, pluginSections, sectionOptions, setOption

try:
	import json
except ImportError:
	import simplejson as json

class ConfigPluginSite(JsonAdminSite):
	def __init__(self, plugin_name):
		JsonAdminSite.__init__(self)
		self.plugin_name = plugin_name
	def render_admin_JSON(self, request):
		return json.dumps({
			'plugin': self.plugin_name,
			'sections': pluginSections(self.plugin_name)
			})

class ConfigSectionSite(JsonAdminSite):
	def __init__(self, plugin_name, section_name):
		JsonAdminSite.__init__(self)
		self.plugin_name = plugin_name
		self.section_name = section_name
	def render_admin_JSON(self, request):
		return json.dumps({
			'plugin': self.plugin_name,
			'section': self.section_name,
			'options': sectionOptions(self.plugin_name, self.section_name)
			})

def init(site):
	configSite = JsonAdminSite()
	for name in pluginNames():
		pluginConfigSite = ConfigPluginSite(name)
		for section in pluginSections(name):
			pluginConfigSite.putChild(section, ConfigSectionSite(name, section))
		configSite.putChild(name, pluginConfigSite)
	site.putChild('config', configSite)

