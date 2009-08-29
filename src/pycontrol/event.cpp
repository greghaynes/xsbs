#include "event.h"

namespace SbPyControl
{

Event::Event(const char *category,
			 const char *name)
: _category(category)
, _name(name)
{
}

const char *Event::category() const
{
	return _category.c_str();
}

const char *Event::name() const
{
	return _name.c_str();
}

}
