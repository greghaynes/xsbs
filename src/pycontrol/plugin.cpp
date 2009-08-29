#include "plugin.h"

namespace SbPyControl
{

PluginEventHandler::PluginEventHandler()
{
}

PluginEventHandler::~PluginEventHandler()
{
}

void PluginEventHandler::setEvent(const char *event)
{
	_event = event;
}

const char *PluginEventHandler::event() const
{
	return _event.c_str();
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

std::vector<PluginEventHandler*> &Plugin::eventHandlers()
{
	return _eventHandlers;
}
	
}
