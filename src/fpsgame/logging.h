/*

  This file is not part of the original Sauerbraten source code.

 */

/*
 *   Copyright (C) 2009 Gregory Haynes <greg@greghaynes.net>
 *
 *   This file is released under the ZLIB license.  See LICENSE.txt
 *   for more information.
 */

#ifndef SB_LOGGING_H
#define SB_LOGGING_H

#include <stdio.h>

namespace server
{

/**
 * @brief A very simple logging class.
 */
class Log
{
	public:
		Log();
		~Log();
		
		bool open(const char *path);
		bool isOpen() const;
		bool write(const char *text);
		void flush();
		FILE *file();

	private:
		FILE *fd;

};

}

#endif
