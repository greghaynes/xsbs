#include "eventmanager.h"

namespace SbPyControl
{


EventManager &EventManager::instance()
{
	static EventManager _instance;
	return _instance;
}

}