#include <vector>

#ifndef SBPY_EVENT_TABLE_H
#define SBPY_EVENT_TABLE_H

namespace SbPyControl
{

class PluginEventHandler;

class EventTable
{

	public:
		EventTable();
		~EventTable();
		
		void registerHandler(const char *event, const PluginEventHandler &handler);
		std::vector<const PluginEventHandler*> handlers(const char *event);
		void clear();
	
	private:
		unsigned char hash(const char *str) const;
	
		std::vector<const PluginEventHandler*> *eventHandlers[255];

};

}

#endif