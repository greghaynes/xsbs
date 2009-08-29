#include "eventtable.h"

#include <strings.h>

namespace SbPyControl
{

EventTable::EventTable()
{
	bzero(eventHandlers, sizeof(void*)*255);
}

EventTable::~EventTable()
{
	clear();
}

void EventTable::clear()
{
	int i;
	for(i = 0; i < 255; i++)
	{
		if(eventHandlers[i])
			delete eventHandlers[i];
	}
}

}