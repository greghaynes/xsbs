#include "pluginmanager.h"
#include "game.h"

#include <vector>

namespace SbPyControl
{

class Event;
class PluginHandler;

class EventManager
{

	public:
		static EventManager &instance();
		
		void registerHandler(const PluginHandler &handler, const Event &event);
		std::vector<PluginHandler*> handlers(const Event &event);
		
	private:
		std::vector<Event*> events;
		hashtable<char*, std::vector<PluginHandler*> > event_handlers;

};

}