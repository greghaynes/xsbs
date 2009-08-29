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
	std::cout << "Loading plugins...\n";
	clearPlugins();
	std::vector<std::string> *pluginPaths;
	std::vector<std::string>::iterator itr;
	std::vector<std::string>::iterator itr2;
	for(itr = paths().begin(); itr != paths().end(); itr++)
	{
		std::cout << "Checking path: " << *itr << "\n";
		pluginPaths = dirsIn(*itr);
		for(itr2 = pluginPaths->begin(); itr2 != pluginPaths->end(); itr2++)
		{
			std::cout << "Found plugin: " << *itr2 << "\n";
		}
		delete pluginPaths;
	}
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