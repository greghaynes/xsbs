#include "pluginmanager.h"
#include "game.h"

#include <vector>

namespace SbPyControl
{

class PluginHandler;

class Event
{
	public:
		Event(const char *category,
			const char *name);
};

class EventManager
{

	public:
		static EventManager &instance();
		
		void registerHandler(const PluginHandler &);
		
	private:
		bool event_exists(const char *event);
	
		std::vector<char*> events;
		hashtable<const char*, std::vector<PluginHandler*> > event_handlers;

};

}