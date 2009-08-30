#include "pluginmanager.h"
#include "plugin.h"

#include <sys/types.h>
#include <sys/dir.h>
#include <dirent.h>

#include <iostream>

namespace SbPyControl
{

PluginManager &PluginManager::instance()
{
	static PluginManager _instance;
	return _instance;
}

PluginManager::PluginManager()
{
}

PluginManager::~PluginManager()
{
	clearPlugins();
}

std::vector<std::string> &PluginManager::paths()
{
	return _paths;
}

void PluginManager::reload()
{
	std::vector<std::string> *pluginPaths, *tmpPaths;
	std::vector<std::string>::iterator itr, itr2;
	Plugin *plugin;
	
	std::cout << "Loading plugins...\n";
	clearPlugins();
	
	pluginPaths = new std::vector<std::string>;
	for(itr = paths().begin(); itr != paths().end(); itr++)
	{
		tmpPaths = dirsIn(*itr);
		for(itr2 = tmpPaths->begin(); itr2 != tmpPaths->end(); itr2++)
		{
			pluginPaths->push_back(*itr2);
		}
		delete tmpPaths;
	}
	
	for(itr = pluginPaths->begin(); itr != pluginPaths->end(); itr++)
	{
		plugin = pluginFromPath(*itr);
		if(plugin)
			_plugins.push_back(plugin);
		else
			std::cout << "Error loading plugin: " << *itr << "\n";

	}
	delete pluginPaths;
}

const std::vector<Plugin*> &PluginManager::plugins() const
{
	return _plugins;
}

Plugin *PluginManager::pluginFromPath(const std::string &path)
{
	return 0;
}

void PluginManager::clearPlugins()
{
	std::vector<Plugin*>::iterator itr;
	for(itr = _plugins.begin(); itr != _plugins.end(); itr++)
	{
		delete *itr;
	}
}

std::vector<std::string> *PluginManager::dirsIn(const std::string &path)
{
	std::vector<std::string> *dirs;
	std::string str;
	struct dirent *de;
	DIR *dir = opendir(path.c_str());
	if(!dir)
		return 0;
	dirs = new std::vector<std::string>;
	while(de = readdir(dir))
	{
		if(de->d_type == DT_DIR
		   && de->d_name[0] != '.')
		{
			str = path;
			if(str.length() == 0 || str[str.length()-1] != '/')
				str.append("/");
			str.append(de->d_name);
			dirs->push_back(str);
		};
	}
	return dirs;
}

}