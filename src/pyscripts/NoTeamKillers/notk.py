from Bans.bans import ban
from xsbs.settings import PluginConfig
from xsbs.events import registerServerEventHandler
from xsbs.players import masterRequired, player
from xsbs.ui import notice, warning, error
from xsbs.colors import colordict
from xsbs.commands import commandHandler, UsageError, ArgumentValueError
from xsbs.server import message as serverMessage
import sbserver
import string

config = PluginConfig('notk')
limit = int(config.getOption('Config', 'teamkill_limit', '5'))
duration = int(config.getOption('Config', 'ban_time', '3600'))
warn_tk_limit = config.getOption('Config', 'warn_tk_limit', 'no') == 'yes'
warn_tk_message = config.getOption('Config', 'warn_tk_message', 'This server does not allow more than ${red}${limit}${white} teamkills per game')
del config
warn_tk_message = string.Template(warn_tk_message)
enableTeamKillLimit = True

def onTeamkill(cn, tcn):
        global enableTeamKillLimit
        if enableTeamKillLimit == True:
                sbserver.message(notice('Team-kill limit is enabled'))
                if player(cn).teamkills() >= limit:
                        ban(cn, duration, 'killing teammates', -1)
                elif warn_tk_limit and player(cn).teamkills() == 1:
                        player(cn).message(warning(warn_tk_message.substitute(colordict, limit=limit)))

registerServerEventHandler('player_teamkill', onTeamkill)

@commandHandler('disabletklimit')
@masterRequired
def onDisableTeamKillLimitCommand(cn, args):
	'''@description Disable the team-kill limit
	   @usage '''
	global enableTeamKillLimit
	enableTeamKillLimit = False
	sbserver.message(notice('Team-kill limit disabled'))

@commandHandler('enabletklimit')
@masterRequired
def onEnableTeamKillLimitCommand(cn, args):
	'''@description Enable the team-kill limit
	   @usage '''
	global enableTeamKillLimit
	enableTeamKillLimit = True
	sbserver.message(notice('Team-kill limit enabled'))

@commandHandler('cleartks')
@masterRequired
def onClearTksCommand(cn, args):
	'''@description Clear (reset) team-kill counter for a player
	   @usage <cn>'''
	tcn = int(args)
	t = player(tcn)
	serverMessage(info(kick_message.substitute(colordict, name=p.name())))
	t.kick()

