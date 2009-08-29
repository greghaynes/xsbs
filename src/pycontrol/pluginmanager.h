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
		
		const std::vector<Plugin*> &plugins() const;
	
	private:
		PluginManager();
		~PluginManager();
		
		std::vector<Plugin*> _plugins;
		std::string _path;
	
};

}

#endif
