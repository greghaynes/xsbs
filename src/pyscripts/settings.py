from ConfigParser import ConfigParser

configuration_folder = 'Config'
configuration_extension = '.conf'

def loadConfigFile(name):
	path = configuration_folder
	if name[0] != '/' and configuration_folder[len(configuration_folder)-1] != '/':
		path += '/'
	path += name
	path += configuration_extension
	config = ConfigParser()
	config.read(path)
	return config

