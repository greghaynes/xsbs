#ifndef SBCS_H
#define SBCS_H

#include <string>

namespace SbCs
{
	char * cseval(std::string data);
	void   trigger_event(std::string eventname, std::string args[], size_t num_args);
	void   deinitCs();
	void   initCs();
}

#endif // SBCS_H