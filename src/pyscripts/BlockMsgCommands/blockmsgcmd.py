import sbevents
from ConfigParser import ConfigParser

prefixes = []

def allowMsg(cn, text):
	if prefixes.find(text[0]) != -1:
		return False
	return True

conf = ConfigParser()
if conf.read('BlockMsgCommands/plugin.conf') and conf.get('Config', 'prefixes'):
	prefixes = conf.get('Config', 'prefixes').strip(' ,')
	sbevents.registerPolicyEventHandler("allow_message", allowMsg)
	sbevents.registerPolicyEventHandler("allow_message_team", allowMsg)
else:
	print 'BlockMsgCommands plugin could not read config file'
