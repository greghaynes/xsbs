#ifndef SBPY_PLUGIN_H
#define SBPY_PLUGIN_H

#include <string>

namespace SbPyControl
{

class Event;

class PluginHandler
{
	public:
		PluginHandler();
		~PluginHandler();
		
		Event *event() const;
		void setEvent(Event *event);
		const char *module() const;
		void setModule(const char *module);
		const char *handler() const;
		void setHandler(const char *function);
		
	private:
		Event *_event;
		std::string _module;
		std::string _handler;
	
};

class Plugin
{
	public:
		explicit Plugin(const char *name);
		
		const char *name() const;
	
	private:
		std::string _name;
	
};

}

#endif

