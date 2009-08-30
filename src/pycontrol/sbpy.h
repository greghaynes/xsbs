#ifndef SBPY_SBPY_H
#define SBPY_SBPY_H

#include <Python.h>
#include <vector>

namespace SbPy
{

bool initPy();
void deinitPy();
bool triggerEvent(const char *event_name, std::vector<PyObject*> *args);
bool triggerEventInt(const char *event_name, int cn);
bool triggerEventIntString(const char *event_name, int cn, const char *text);

}

#endif