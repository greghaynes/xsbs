from elixir import setup_all, create_all
import os, sys

# Initialize these before loading plugins
import xsbs.db
import xsbs.events
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

class PluginManager(object):
	def __init__(self, plugins_path='plugins'):
		self.plugins_path = plugins_path
		self.plugin_modules = []
	def loadPlugins(self):
		files = os.listdir(self.plugins_path)
		for file in files:
			if file[0] != '.':
				self.plugin_modules.append(__import__(os.path.basename(self.plugins_path) + '.' + os.path.splitext(file)[0]))

def main():
	pm = PluginManager()
	pm.loadPlugins()
	setup_all()
	create_all()

main()

