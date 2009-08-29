#ifndef SBPY_EVENT_H
#define SBPY_EVENT_H

#include <string>

namespace SbPyControl
{
	
class Event
{
	public:
		enum Category {
			Server,
			Player
		};
	
		Event(Category category,
			  const char *name);
		
		const char *category() const;
		const char *name() const;
		
	private:
		std::string _category;
		std::string _name;
};

}

#endif
