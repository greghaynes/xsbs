modes = [
	'ffa',
	'coop',
	'team',
	'insta',
	'instateam',
	'effic',
	'efficteam',
	'tac',
	'tacteam',
	'capture',
	'regencapture',
	'ctf',
	'instactf',
	'protect',
	'instaprotect'
]

def modeNumber(modename):
	i = 0
	for mode in modes:
		if modename == mode:
			return i
		i += 1
	raise ValueError('Invalid mode')

