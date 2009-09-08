def textcolor(color, text):
	if text:
		return '\fs\f' + str(color) + text + '\fr'
	else:
		return '\f' + str(color)
def green(text=None):
	return textcolor(0, text)
def blue(text=None):
	return textcolor(1, text)
def yellow(text=None):
	return textcolor(2, text)
def red(text=None):
	return textcolor(3, text)
def magenta(text=None):
	return textcolor(5, text)
def orange(text=None):
	return textcolor(6, text)
def white(text=None):
	return textcolor(10, text)

colordict = { 'green': green(),
	'blue' : blue(),
	'yelllow' : yellow(),
	'red' : red(),
	'magenta': magenta(),
	'orange': orange(),
	'white': white() }

def colorstring(str, text):
	if str == 'green':
		return green(text)
	if str == 'blue':
		return blue(text)
	if str == 'yellow':
		return yellow(text)
	if str == 'red':
		return red(text)
	if str == 'magenta':
		return magenta(text)
	if str == 'orange':
		return orange(text)
	if str == 'white':
		return white(text)

def ipLongToString(num):
	return '%d.%d.%d.%d' % ((num & 0xff),
		(num >> 8) & 0xff,
		(num >> 16) & 0xff,
		(num >> 24) & 0xff)

