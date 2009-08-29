#ifndef SBPY_PLUGIN_H
#define SBPY_PLUGIN_H

#include <string>
#include <vector>

namespace SbPyControl
{

class Event;

class PluginEventHandler
{
	public:
		PluginEventHandler();
		~PluginEventHandler();

		void setEvent(Event *event);
		const Event *event() const;
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
		const std::vector<PluginEventHandler*> eventHandlers;
	
	private:
		std::string _name;
	
};

}

#endif

