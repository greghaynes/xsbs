import sbevents, sbserver, sbtools
import urllib2, urllib
jsonlib = None
try:
	import json #standard in python 2.6
	jsonlib = json
except:
        try:
                import simplejson
                jsonlib =  simplejson
        except:
                pass

#If Google changes behaviour this script will stop working.

url = "http://ajax.googleapis.com/ajax/services/language/translate"
headers = {'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.1) Gecko/20061205 Iceweasel/2.0.0.1 (Debian-2.0.0.1+dfsg-2)'}
langs = ['af','sq','am','ar','hy',
		'az','eu','be','bn','bh','bg','my',
		'ca','chr','zh','zh-CN','zh-TW',
		'hr','cs','da','dv','nl','en',
		'eo','et','tl','fi','fr','gl',
		'ka','de','el','gn','gu','iw',
		'hi','hu','is','id','iu','ga',
		'it','ja','kn','kk','km','ko',
		'ku','ky','lo','lv','lt','mk',
		'ms','ml','mt','mr','mn','ne',
		'no','or','ps','fa','pl','pt-PT',
		'pa','ro','ru','sa','sr','sd',
		'si','sk','sl','es','sw','sv',
		'tg','ta','tl','te','th','bo',
		'tr','uk','ur','uz','ug','vi',
		'cy','yi']

class Translator:
	def __init__(self, url, headers, langs):
		self.url = url
		self.headers = headers
		self.langs = langs

	def translate(self,word, from_lang = "en", to_lang = "sv"):#Default is english to swedish conversion
		values = {"langpair":"%s|%s" %(from_lang,to_lang), "ie":"UTF8", "oe":"UTF8", "v":"1.0", "q":word}
		data = urllib.urlencode(values)
		request = urllib2.Request(self.url, data, self.headers)
		response = urllib2.urlopen(request)
		try:
			#TODO: character conversion needed here, sauerbraten doesn't handle utf8
			return "Translation: %s" % ( jsonlib.loads(response.read())["responseData"]["translatedText"] )
		except Exception:
			return "Could not translate"

	def is_lang(self,s):
		for lang in self.langs:
			if lang.lower() == s.lower():
				return True
		return False
	
	def sentence(self,list_of_strings):
		str = ""
		for s in list_of_strings:
			str += s + " "
		return str

translator = Translator(url, headers, langs)

def onCommand(cn, command):
	cmd_list = command.split()
	length = len(cmd_list)
	if length == 0:
		sbserver.playerMessage(cn, sbtools.red("Usage: #trans <word> or #trans <sentence/word> <from_lang> <to_lang> Language codes: en, sv, de, it and lots more."))
	elif length == 1:
		sbserver.message(translator.translate(cmd_list[0]))
	elif length > 2:
		if translator.is_lang(cmd_list[length-2]) and translator.is_lang(cmd_list[length-1]):
			translation = translator.translate(translator.sentence(cmd_list[:length-2]),cmd_list[length-2],cmd_list[length-1])
			sbserver.message(translation)

if jsonlib == None:
	print "Python json library not present. Can't use #trans."
else:
	sbevents.registerCommandHandler('trans', onCommand)
