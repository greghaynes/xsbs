#include <string>
#include <vector>

#ifndef SBPY_PLUGINMANAGER_H
#define SBPY_PLUGINMANAGER_H

namespace SbPyControl
{

class Plugin;

class PluginManager
{
	public:
		static PluginManager &instance();
		
		std::vector<std::string> &paths();
		void reload();
		const std::vector<Plugin*> &plugins() const;
	
	private:
		PluginManager();
		~PluginManager();
		
		void clearPlugins();
		std::vector<std::string> *dirsIn(const std::string &path);
		
		std::vector<std::string> _paths;
		std::vector<Plugin*> _plugins;
		std::string _path;
	
};

}

#endif
