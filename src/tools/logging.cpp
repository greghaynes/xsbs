/*
 *   Copyright (C) 2009 Gregory Haynes <greg@greghaynes.net>
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program; if not, write to the
 *   Free Software Foundation, Inc.,
 *   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
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
