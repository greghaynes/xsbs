#include "plugin.h"
#include "eventmanager.h"
#include "event.h"

namespace SbPyControl
{

PluginEventHandler::PluginEventHandler()
{
}

PluginEventHandler::~PluginEventHandler()
{
	if(_event)
		delete _event;
}

void PluginEventHandler::setEvent(Event *event)
{
	if(_event && event != _event)
		delete _event;
	_event = event;
}

const Event *PluginEventHandler::event() const
{
	return _event;
}

const char *PluginEventHandler::module() const
{
	return _module.c_str();
}

void PluginEventHandler::setModule(const char *module)
{
	_module = module;
}

const char *PluginEventHandler::handler() const
{
	return _handler.c_str();
}

void PluginEventHandler::setHandler(const char *handler)
{
	_handler = handler;
}

Plugin::Plugin(const char *name)
: _name(name)
{
}

const char *Plugin::name() const
{
	return _name.c_str();
}
	
}
