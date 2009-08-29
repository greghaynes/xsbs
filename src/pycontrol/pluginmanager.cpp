#include "pluginmanager.h"

#include <string.h>

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
}

}