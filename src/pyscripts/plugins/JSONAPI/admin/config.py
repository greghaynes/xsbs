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
		for section in pluginSections(plugin_name):
			self.putChild(section, ConfigSectionSite(plugin_name, section))
	def render_admin_JSON(self, request, user):
		return json.dumps({
			'plugin': self.plugin_name,
			'sections': pluginSections(self.plugin_name)
			})

class ConfigSectionSite(JsonAdminSite):
	def __init__(self, plugin_name, section_name):
		JsonAdminSite.__init__(self)
		self.plugin_name = plugin_name
		self.section_name = section_name
	def render_admin_JSON(self, request, user):
		return json.dumps({
			'plugin': self.plugin_name,
			'section': self.section_name,
			'options': sectionOptions(self.plugin_name, self.section_name)
			})

class ConfigSite(JsonAdminSite):
	def __init__(self):
		JsonAdminSite.__init__(self)
		self.plugin_names = []
		for name in pluginNames():
			pluginConfigSite = ConfigPluginSite(name)
			self.putChild(name, pluginConfigSite)
			self.plugin_names.append(name)
	def render_admin_JSON(self, request, user):
		return json.dumps({
			'plugins': self.plugin_names
			})

def setup(site):
	configSite = ConfigSite()
	site.putChild('config', configSite)

