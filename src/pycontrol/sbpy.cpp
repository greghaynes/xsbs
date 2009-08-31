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

#include "sbpy.h"

#include <string>
#include <iostream>

namespace SbPy
{

#define SBPY_ERR(x) \
	if(!x) \
	{ \
		if(PyErr_Occurred()) \
			PyErr_Print(); \
		return false;\
	}

static PyObject *eventsModule, *triggerEventFunc, *triggerPolicyEventFunc;

bool initPy(const char *pyscripts_path)
{
	PyObject *pFunc, *pArgs, *pValue, *pluginsModule;
	
	std::string path;
	pluginsModule = PyImport_ImportModule("sbplugins");
	SBPY_ERR(pluginsModule)
	eventsModule = PyImport_ImportModule("sbevents");
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
	triggerEventFunc = PyObject_GetAttrString(eventsModule, "triggerEvent");
	SBPY_ERR(triggerEventFunc);
	if(!PyCallable_Check(triggerEventFunc))
	{
		fprintf(stderr, "Error: triggerEvent function could not be loaded.\n");
		return false;
	}
	triggerPolicyEventFunc = PyObject_GetAttrString(eventsModule, "triggerPolicyEvent");
	SBPY_ERR(triggerPolicyEventFunc);
	if(!PyCallable_Check(triggerPolicyEventFunc))
	{
		fprintf(stderr, "Error: triggerPolicyEvent function could not be loaded.\n");
		return false;
	}
	Py_DECREF(pluginsModule);
	
	return true;
}

void deinitPy()
{
	Py_Finalize();
}

bool triggerFuncEvent(const char *name, std::vector<PyObject*> *args, PyObject *func)
{
	PyObject *pArgs, *pArgsArgs, *pName, *pValue;
	std::vector<PyObject*>::const_iterator itr;
	int i = 0;
	
	if(!func)
	{
		std::cout << "Invalid function handler to trigger event.\n";
		return false;
	}
	pArgs = PyTuple_New(2);
	pName = PyString_FromString(name);
	SBPY_ERR(pName)
	PyTuple_SetItem(pArgs, 0, pName);
	if(args)
	{
		pArgsArgs = PyTuple_New(args->size());
		for(itr = args->begin(); itr != args->end(); itr++)
		{
			PyTuple_SetItem(pArgsArgs, i, *itr);
			i++;
		}
	}
	else
		pArgsArgs = PyTuple_New(0);
	PyTuple_SetItem(pArgs, 1, pArgsArgs);
	pValue = PyObject_CallObject(func, pArgs);
	Py_DECREF(pArgs);
	if(!pValue)
	{
		PyErr_Print();
		fprintf(stderr, "Error triggering event.\n");
		return false;
	}
	if(PyBool_Check(pValue))
	{
		bool ret = (pValue == Py_True);
		Py_DECREF(pValue);
		return ret;
	}
	Py_DECREF(pValue);
	return true;
}

#undef SBPY_ERR

bool triggerFuncEventInt(const char *name, int cn, PyObject *func)
{
	std::vector<PyObject*> args;
	PyObject *pCn = PyInt_FromLong(cn);
	args.push_back(pCn);
	return triggerFuncEvent(name, &args, func);
}

bool triggerFuncEventIntString(const char *name, int cn, const char *text, PyObject *func)
{
	std::vector<PyObject*> args;
	PyObject *pText = PyString_FromString(text);
	PyObject *pCn = PyInt_FromLong(cn);
	args.push_back(pCn);
	args.push_back(pText);
	return triggerFuncEvent(name, &args, func);
}

bool triggerEvent(const char*name, std::vector<PyObject*>* args)
{
	return triggerFuncEvent(name, args, triggerEventFunc);
}

bool triggerEventInt(const char *name, int cn)
{
	return triggerFuncEventInt(name, cn, triggerEventFunc);
}

bool triggerEventIntString(const char *name, int cn, const char *text)
{
	return triggerFuncEventIntString(name, cn, text, triggerEventFunc);
}

bool triggerEventIntInt(const char *name, int cn1, int cn2)
{
	std::vector<PyObject*> args;
	PyObject *pCn1 = PyInt_FromLong(cn1);
	PyObject *pCn2 = PyInt_FromLong(cn2);
	args.push_back(pCn1);
	args.push_back(pCn2);
	return triggerFuncEvent(name, &args, triggerEventFunc);
}

bool triggerPolicyEventInt(const char *name, int cn)
{
	return triggerFuncEventInt(name, cn, triggerPolicyEventFunc);
}

bool triggerPolicyEventIntString(const char *name, int cn, const char *text)
{
	return triggerFuncEventIntString(name, cn, text, triggerPolicyEventFunc);
}

}
