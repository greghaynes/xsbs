import sbevents
from ConfigParser import ConfigParser

prefixes = []

def allowMsg(cn, text):
	if prefixes.has_key(text[0]):
		return False
	return True

conf = ConfigParser()
if conf.read('BlockMsgCommands/plugin.conf') and conf.get('Config', 'prefixes'):
	prefixes = conf.get('Config', 'prefixes')
	sbevents.registerPolicyEventHandler("allow_message", allowMsg)
	sbevents.registerPolicyEventHandler("allow_message_team", allowMsg)
