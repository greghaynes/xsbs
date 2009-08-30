#include "sbpy.h"

#include <string>
#include <iostream>

namespace SbPyModule
{

static PyObject *pluginsModule, *eventsModule;

PyMODINIT_FUNC initsbpy()
{
}

#define SBPY_ERR(x) \
	if(!x) \
	{ \
		if(PyErr_Occurred()) \
			PyErr_Print(); \
		return false;\
	}

bool initPy(const char *prog_name, const char *pyscripts_path)
{
	PyObject *pFunc, *pArgs, *pValue, *triggerFunc;
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
	SBPY_ERR(pluginsModule)
	eventsModule = PyImport_ImportModule("events");
	SBPY_ERR(eventsModule)
	pFunc = PyObject_GetAttrString(pluginsModule, "loadPlugins");
	SBPY_ERR(pFunc)
	if(!PyCallable_Check(pFunc))
	{
		fprintf(stderr, "Error: loadPlugins function could not be loaded.\n");
		return false;
	}
	pArgs = PyTuple_New(0);
	pValue = PyObject_CallObject(pFunc, pArgs);
	Py_DECREF(pArgs);
	Py_DECREF(pFunc);
	if(!pValue)
	{
		PyErr_Print();
		return false;
	}
	Py_DECREF(pValue);
	triggerFunc = PyObject_GetAttrString(eventsModule, "triggerEvent");
	SBPY_ERR(triggerFunc);
	if(!PyCallable_Check(triggerFunc))
	{
		fprintf(stderr, "Error: triggerEvent function could not be loaded.\n");
		return false;
	}
	Py_DECREF(triggerFunc);
	delete pn;
	
	return true;
}

void deinitPy()
{
	Py_Finalize();
}

bool triggerEvent(const char *name, std::vector<PyObject*> &args)
{
	PyObject *pArgs, *pName, *pValue, *pFunc;
	std::vector<PyObject*>::const_iterator itr;
	int i = 1;
	
	pArgs = PyTuple_New(1);
	pName = PyString_FromString("server_start");
	PyTuple_SetItem(pArgs, 0, pName);
	/*
	for(itr = args.begin(); itr != args.end(); itr++)
	{
		PyTuple_SetItem(pArgs, i, *itr);
		i++;
	}
	*/
	pFunc = PyObject_GetAttrString(eventsModule, "triggerEvent");
	SBPY_ERR(pFunc)
	pValue = PyObject_CallObject(pFunc, pArgs);
	Py_DECREF(pFunc);
	Py_DECREF(pName);
	Py_DECREF(pArgs);
	if(!pValue)
	{
		PyErr_Print();
		return false;
	}
	Py_DECREF(pValue);
	return true;
}

#undef SBPY_ERR

}