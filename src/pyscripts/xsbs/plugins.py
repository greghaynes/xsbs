from ConfigParser import ConfigParser, NoOptionError
import os, sys, __builtin__
import sbserver, xsbs.events

# Initialize these before loading plugins
import xsbs.log
import xsbs.ban
import xsbs.users
import xsbs.server
import xsbs.game
import xsbs.teamcontrol
import xsbs.persistteam
import xsbs.demo
import xsbs.http
import xsbs.http.jsonapi

import logging

plugins = {}
paths = [os.curdir]
config_filename = 'plugin.conf'
init_modules = sys.modules.keys()

class Plugin:
	def __init__(self, path, config_path):
		self.path = path
		conf = ConfigParser()
		conf.read(config_path)
		self.isenabled = True
		try:
			self.initmodule = conf.get('Plugin', 'module')
			self.isenabled = (conf.get('Plugin', 'enable') == 'yes')
			self.name = conf.get('Plugin', 'name')
			self.version = conf.get('Plugin', 'version')
			self.author = conf.get('Plugin', 'author')
		except NoOptionError:
			self.isenabled = False
		del conf
	def loadModule(self):
		if self.initmodule and self.isenabled:
			self.module = __import__(os.path.basename(self.path) + '.' + self.initmodule)
	def unloadModule(self):
		if self.isenabled:
			del self.module
	def enabled(self):
		return self.isenabled

def plugin(name):
	return plugins[name]

def loadPlugins():
	plugins.clear()
	logging.info('Loading plugins...')
	for path in paths:
		files = os.listdir(path)
		for file in files:
			dirpath = path + '/' + file
			config_path = dirpath + '/' + config_filename
			if os.path.isdir(dirpath) and os.path.exists(config_path):
				p = Plugin(dirpath, config_path)
				if p.isenabled:
					plugins[p.name] = p
				else:
					logging.info('Skipping %s plugin' % file)
	logging.info('Found %i plugins' % len(plugins.keys()))
	logging.info('Initializing plugins...')
	for plugin in plugins.values():
		plugin.loadModule()

def reloadPlugins():
	for p in plugins.values():
		p.unloadModule()
	xsbs.events.triggerServerEvent('reload', ())
	for p in plugins.values():
		p.loadModule()

loadPlugins()

