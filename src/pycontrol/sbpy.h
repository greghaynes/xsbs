#ifndef SBPY_SBPY_H
#define SBPY_SBPY_H

#include <Python.h>
#include <vector>

namespace SbPyModule
{

bool initPy(const char *prog_name, const char *pyscripts_path);
void deinitPy();
bool triggerEvent(const char *event_name, std::vector<PyObject*> &args);

}

#endif