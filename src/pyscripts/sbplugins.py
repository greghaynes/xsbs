from ConfigParser import ConfigParser
import os, sys, __builtin__
import sbserver, sbevents

plugins = []
paths = [os.curdir]
config_filename = 'plugin.conf'
init_modules = sys.modules.keys()

class Plugin:
	def __init__(self, path, config_path):
		conf = ConfigParser()
		conf.read(config_path)
		self.initmodule = conf.get('Plugin', 'module')
		if conf.has_option('Plugin', 'enable'):
			self.isenabled = 'yes' == conf.get('Plugin', 'enable')
		else:
			self.isenabled = False
		if self.initmodule and self.isenabled:
			self.module = __import__(os.path.basename(path) + '.' + self.initmodule)
		del conf

def loadPlugins():
	del plugins[:]
	print 'Loading plugins...'
	for path in paths:
		files = os.listdir(path)
		for file in files:
			dirpath = path + '/' + file
			config_path = dirpath + '/' + config_filename
			if os.path.isdir(dirpath) and os.path.exists(config_path):
				plugins.append(Plugin(dirpath, config_path))

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

