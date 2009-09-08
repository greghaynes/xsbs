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

#include "servermodule.h"
#include "server.h"

#include <iostream>

namespace SbPy
{

static char *getStringFromTupleAt(PyObject *pTuple, int n)
{
	PyObject *pStr;
	char *str;
	pStr = PyTuple_GetItem(pTuple, n);
	if(pStr)
	{
		str = PyString_AsString(pStr);
		return str;
	}
	std::cout << "Could not get string.\n";
	return 0;
}

static int getIntFromTupleAt(PyObject *pTuple, int n)
{
	PyObject *pInt;
	pInt = PyTuple_GetItem(pTuple, n);
	n = PyInt_AsLong(pInt);
	return n;
}

static PyObject *numClients(PyObject *self, PyObject *args)
{
	return Py_BuildValue("i", server::numclients());
}

static PyObject *message(PyObject *self, PyObject *args)
{
	PyObject *pMsg = PyTuple_GetItem(args, 0);
	if(pMsg)
	{
		char *msg = PyString_AsString(pMsg);
		if(msg)
			server::sendservmsg(msg);
	}
	else
		fprintf(stderr, "Error sending message");
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *clients(PyObject *self, PyObject *args)
{
	PyObject *pTuple = PyTuple_New(server::numclients());
	PyObject *pInt;
	int y = 0;
	loopv(server::clients)
	{
		pInt = PyInt_FromLong(i);
		PyTuple_SetItem(pTuple, i, pInt);
		y++;
	}
	return pTuple;
}

static PyObject *players(PyObject *self, PyObject *args)
{
	server::clientinfo *ci;
	std::vector<int> spects;
	std::vector<int>::iterator itr;
	PyObject *pTuple;
	PyObject *pInt;
	int y = 0;
	
	loopv(server::clients)
	{
		ci = server::getinfo(i);
		if(ci->state.state != CS_SPECTATOR)
		{
			spects.push_back(i);
		}
	}
	pTuple = PyTuple_New(spects.size());
	
	for(itr = spects.begin(); itr != spects.end(); itr++)
	{
		pInt = PyInt_FromLong(*itr);
		PyTuple_SetItem(pTuple, y, pInt);
		y++;
	}
	return pTuple;
}

static PyObject *spectators(PyObject *self, PyObject *args)
{
	server::clientinfo *ci;
	std::vector<int> spects;
	std::vector<int>::iterator itr;
	PyObject *pTuple;
	PyObject *pInt;
	int y = 0;
	
	loopv(server::clients)
	{
		ci = server::getinfo(i);
		if(ci->state.state == CS_SPECTATOR)
		{
			spects.push_back(i);
		}
	}
	pTuple = PyTuple_New(spects.size());
	
	for(itr = spects.begin(); itr != spects.end(); itr++)
	{
		pInt = PyInt_FromLong(*itr);
		PyTuple_SetItem(pTuple, y, pInt);
		y++;
	}
	return pTuple;
}

static PyObject *playerMessage(PyObject *self, PyObject *args)
{
	int cn = getIntFromTupleAt(args, 0);
	char *text = getStringFromTupleAt(args, 1);
	server::clientinfo *ci = server::getinfo(cn);
	if(ci && ci->state.aitype == AI_NONE)
		sendf(cn, 1, "ris", SV_SERVMSG, text);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *playerName(PyObject *self, PyObject *args)
{
	int cn = getIntFromTupleAt(args, 0);
	server::clientinfo *ci = server::getinfo(cn);
	if(ci && ci->name)
		return Py_BuildValue("s", ci->name);
	else
		std::cout << "Error: Invalid cn or no name assigned to client.";
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *playerIpLong(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn)
	   || !(ci = server::getinfo(cn)))
	{
		Py_INCREF(Py_None);
		return Py_None;
	}
	return Py_BuildValue("i", getclientip(ci->clientnum));
}

static PyObject *playerKick(PyObject *self, PyObject *args)
{
	int cn;
	if(!PyArg_ParseTuple(args, "i", &cn))
	{
		// TODO: Should throw exception
		Py_INCREF(Py_None);
		return Py_None;
	}
	disconnect_client(cn, DISC_KICK);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *playerPrivilege(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn)
	   || !(ci = server::getinfo(cn)))
	{
		Py_INCREF(Py_None);
		return Py_None;
	}
	return Py_BuildValue("i", ci->privilege);
}

static PyObject *playerFrags(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn)
	   || !(ci = server::getinfo(cn)))
	{
		Py_INCREF(Py_None);
		return Py_None;
	}
	return Py_BuildValue("i", ci->state.frags);
}

static PyObject *playerTeamkills(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn)
	   || !(ci = server::getinfo(cn)))
	{
		Py_INCREF(Py_None);
		return Py_None;
	}
	return Py_BuildValue("i", ci->state.teamkills);
}

static PyObject *playerDeaths(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn)
	   || !(ci = server::getinfo(cn)))
	{
		Py_INCREF(Py_None);
		return Py_None;
	}
	return Py_BuildValue("i", ci->state.deaths);
}

static PyObject *playerShots(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn)
	   || !(ci = server::getinfo(cn)))
	{
		Py_INCREF(Py_None);
		return Py_None;
	}
	return Py_BuildValue("i", ci->state.shots);
}

static PyObject *playerHits(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn)
	   || !(ci = server::getinfo(cn)))
	{
		Py_INCREF(Py_None);
		return Py_None;
	}
	return Py_BuildValue("i", ci->state.hits);
}

static PyObject *setBotLimit(PyObject *self, PyObject *args)
{
	int cn, limit;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "ii", &cn, &limit)
	   || !(ci = server::getinfo(cn)))
	{
		Py_INCREF(Py_None);
		return Py_None;
	}
	if(!ci->local && ci->privilege < PRIV_ADMIN)
		sendf(cn, 1, "ris", SV_SERVMSG, "Insufficient permissions to add bot.");
	else
		server::aiman::setbotlimit(ci, limit);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *hashPass(PyObject *self, PyObject *args)
{
	PyObject *pstr;
	int cn;
	char *pass;
	server::clientinfo *ci;
	string string;
	if(!PyArg_ParseTuple(args, "is", &cn, &pass)
		|| !(ci = server::getinfo(cn)))
	{
		Py_INCREF(Py_None);
		return Py_None;
	}
	server::hashpassword(cn, ci->sessionid, pass, string, sizeof(string));
	pstr = PyString_FromString(string);
	return pstr;
}

static PyObject *setMaster(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(PyArg_ParseTuple(args, "i", &cn)
		&& (ci = server::getinfo(cn)))
	{
		server::setcimaster(ci);
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *setAdmin(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(PyArg_ParseTuple(args, "i", &cn)
		&& (ci = server::getinfo(cn)))
	{
		server::setciadmin(ci);
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef ModuleMethods[] = {
	{"numClients", numClients, METH_VARARGS, "Return the number of clients on the server."},
	{"message", message, METH_VARARGS, "Send a server message."},
	{"clients", clients, METH_VARARGS, "List of client numbers."},
	{"players", players, METH_VARARGS, "List of client numbers of active clients."},
	{"spectators", spectators, METH_VARARGS, "List of client numbers of spectating clients."},
	{"playerMessage", playerMessage, METH_VARARGS, "Send a message to player."},
	{"playerName", playerName, METH_VARARGS, "Get name of player from cn."},
	{"playerIpLong", playerIpLong, METH_VARARGS, "Get IP of player from cn."},
	{"playerKick", playerKick, METH_VARARGS, "Kick player from server."},
	{"playerPrivilege", playerPrivilege, METH_VARARGS, "Integer representing player privilege"},
	{"playerFrags", playerFrags, METH_VARARGS, "Number of frags by player in current match."},
	{"playerTeamkills", playerTeamkills, METH_VARARGS, "Number of teamkills by player in current match."},
	{"playerDeaths", playerDeaths, METH_VARARGS, "Number of deatds by player in current match."},
	{"playerShots", playerShots, METH_VARARGS, "Shots by player in current match."},
	{"playerHits", playerHits, METH_VARARGS, "Hits by player in current match."},
	{"setBotLimit", setBotLimit, METH_VARARGS, "Set server bot limit."},
	{"hashPassword", hashPass, METH_VARARGS, "Return hash for user + password"},
	{"setMaster", setMaster, METH_VARARGS, "Set cn to master."},
	{"setAdmin", setAdmin, METH_VARARGS, "Set cn to admin."},
	{NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initModule(const char *module_name)
{
	(void) Py_InitModule(module_name, ModuleMethods);
	return;
}


}
