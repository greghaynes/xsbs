#include "sbpy.h"

#include <string>
#include <iostream>

namespace SbPyModule
{

static PyObject *pluginsModule, *eventsModule;

PyMODINIT_FUNC initsbpy()
{
}

bool initPy(const char *prog_name, const char *pyscripts_path)
{
	std::string path;
	char *pn = new char[strlen(prog_name)+1];
	
	if(-1 == chdir(pyscripts_path))
	{
		perror("Could not chdir into pyscripts folder");
		return false;
	}
	strcpy(pn, prog_name);
	Py_SetProgramName(pn);
	setenv("PYTHONPATH", pyscripts_path, 1);
	Py_Initialize();
	pluginsModule = PyImport_ImportModule("plugins");
	if(!pluginsModule)
	{
		if(PyErr_Occurred())
			PyErr_Print();
		return false;
	}
	eventsModule = PyImport_ImportModule("events");
	if(!eventsModule)
	{
		if(PyErr_Occurred())
			PyErr_Print();
		return false;
	}
	delete pn;
	
	return true;
}

void deinitPy()
{
	Py_Finalize();
}

}