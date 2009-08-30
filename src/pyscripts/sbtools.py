def textcolor(color, text):
	if text:
		return '\fs\f' + color + text + '\fr'
	else
		return '\f' + color
def green(text):
	return textcolor(0, text)
def blue(text):
	return textcolor(1, text)
def yellow(text):
	return textcolor(2, text)
def red(text):
	return textcolor(3, text)
def magenta(text):
	return textcolor(5, text)
def orange(text):
	return textcolor(6, text)
def white(text):
	return textcolor(10, text)
