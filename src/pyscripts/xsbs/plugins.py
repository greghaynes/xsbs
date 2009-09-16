from ConfigParser import ConfigParser, NoOptionError
import os, sys, __builtin__
import sbserver, xsbs.events

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
	def load(self):
		if self.initmodule and self.isenabled:
			self.module = __import__(os.path.basename(self.path) + '.' + self.initmodule)

def plugin(name):
	return plugins[name]

def loadPlugins():
	plugins.clear()
	print 'Loading plugins...'
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
					print 'Skipping %s plugin' % file
	print 'Found %i plugins' % len(plugins.keys())
	print 'Initializing plugins...'
	for plugin in plugins.values():
		plugin.load()

def reload():
	sbevents.triggerEvent('reload', ())
	sbserver.reload()
	return
	for mod in sys.modules.keys():
		print mod
		if mod not in init_modules:
			del sys.modules[mod]
		else:
			print 'skipping ', mod
	loadPlugins()

