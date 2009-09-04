/*
 
 This file is not part of the original Sauerbraten source code.
 
 */

/*
 *   Copyright (C) 2009 Gregory Haynes <greg@greghaynes.net>
 *
 *   This file is released under the ZLIB license.  See LICENSE.txt
 *   for more information.
 */

#include "logging.h"

#include <unistd.h>
#include <string.h>

namespace server
{

Log::Log()
	: fd(0)
{
}

Log::~Log()
{
	if(isOpen())
		fclose(file());
}

bool Log::open(const char *path)
{
	fd = fopen(path, "a");
	return isOpen();
}

bool Log::isOpen() const
{
	return (fd != 0);
}

bool Log::write(const char *text)
{
	ssize_t len;
	if(!isOpen())
	{
		puts("Cannot write to closed log.\n");
		return false;
	}
	len = strlen(text);
	return fwrite(text, len, 1, file()) == len;
}

void Log::flush()
{
	fflush(file());
}

FILE *Log::file()
{
	return fd;
}

}