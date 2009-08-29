#include "plugin.h"
#include "event.h"

namespace SbPyControl
{

const char *Plugin::name() const
{
	return _name.c_str();
}

PluginHandler::PluginHandler()
: _event(0)
{
}

PluginHandler::~PluginHandler()
{
	if(_event)
		delete _event;
}

Event *PluginHandler::event() const
{
	return _event;
}

void PluginHandler::setEvent(Event *event)
{
	if(_event)
		delete _event;
	_event = event;
}

const char *PluginHandler::module() const
{
	return _module.c_str();
}

void PluginHandler::setModule(const char *module)
{
	_module = module;
}

const char *PluginHandler::handler() const
{
	return _handler.c_str();
}

void PluginHandler::setHandler(const char *handler)
{
	_handler = handler;
}

Plugin::Plugin(const char *name)
: _name(name)
{
}
	
}
