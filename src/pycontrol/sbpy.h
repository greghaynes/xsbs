#ifndef SBPY_SBPY_H
#define SBPY_SBPY_H

#include "Python.h"

namespace SbPyModule
{

bool initPy(const char *prog_name, const char *pyscripts_path);
void deinitPy();

}

#endif