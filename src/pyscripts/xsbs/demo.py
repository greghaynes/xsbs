import sbserver
from xsbs.events import eventHandler
from xsbs.ui import notice
from xsbs.settings import PluginConfig
from xsbs.colors import colordict
from UserPrivilege.userpriv import masterRequired
import string

config = PluginConfig('demorecord')
action_temp = config.getOption('Config', 'record_next_message', 'Demo recording is ${action} for next match (by ${orange}${user}${white}${white}${white}${white})')
del config
action_temp = string.Template(action_temp)

@eventHandler('player_record_demo')
@masterRequired
def playerRecordNextMatch(cn, val):
	if val == sbserver.nextMatchRecorded():
		return
	if val:
		act = 'enabled'
	else:
		act = 'disabled'
	sbserver.setRecordNextMatch(val)
	sbserver.message(notice(action_temp.substitute(colordict, action=act, user=sbserver.playerName(cn))))

