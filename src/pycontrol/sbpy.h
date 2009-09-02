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

#ifndef SBPY_SBPY_H
#define SBPY_SBPY_H

#include <Python.h>
#include <vector>

namespace SbPy
{

bool initPy(const char *pyscripts_path);
void deinitPy();
bool triggerEvent(const char *event_name, std::vector<PyObject*> *args);
bool triggerEventInt(const char *event_name, int cn);
bool triggerEventIntString(const char *event_name, int cn, const char *text);
bool triggerEventIntInt(const char *name, int cn1, int cn2);
bool triggerPolicyEventInt(const char *name, int cn);
bool triggerPolicyEventIntString(const char *event_name, int cn, const char *text);
void triggerExecQueue();

}
#endif
