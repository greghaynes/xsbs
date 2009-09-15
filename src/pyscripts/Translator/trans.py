import sbserver
from xsbs.commands import registerCommandHandler
from xsbs.colors import red
import socket, re, asyncore

#If Google changes behaviour this script will stop working.
query=""
from_lang=""
to_lang="" 

url = "http://ajax.googleapis.com/ajax/services/language/translate"
langslist = ['af','sq','am','ar','hy',
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
host = 'ajax.googleapis.com'
port = 80
header = """GET http://ajax.googleapis.com/ajax/services/language/translate?langpair=%s|%s&v=1.0&q=%s HTTP/1.1

"""

class SocketDispatch(asyncore.dispatcher):
	def __init__(self, host, port, header):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect((host, port))
		self.setblocking(0)
		self.buff = ''
		self.writebuff = ''
		begin = 'translatedText\":\"'
		end = '\"'
		self.pattern = re.compile(begin+"(.*?)"+end, re.DOTALL)
	def __del__(self):
		self.close
	def handle_connect(self):
		pass
	def handle_write(self):
		sent = self.send(self.writebuff)
		self.writebuff = self.writebuff[sent:]
	def writeable(self):
		return len(self.writebuff) > 0
	def handle_read(self):
		self.buff += self.recv(4096)
		if self.buff != "":
			m = re.search(self.pattern, self.buff)
			self.buff = ""
			try:
				sbserver.message(m.group(1))
			except:
				sbserver.playerMessage(cn,"Translation failed")
	def write(self,query, from_lang="en", to_lang="sv"):
		self.writebuff += header % (from_lang, to_lang, query)
		self.handle_write()

sd = SocketDispatch(host, port, header)

def is_lang(s,langs):
	for lang in langs:
		if lang.lower() == s.lower():
			return True
	return False

def onCommand(cn, command):
	cmd_list = command.split()
	length = len(cmd_list)
	if length == 0:
		sbserver.playerMessage(cn, red("Usage: #trans <word> or #trans <sentence/word> <from_lang> <to_lang> Language codes: en, sv, de, it and lots more."))
	elif length == 1:
		sd.write(cmd_list[0])
	elif length > 2:
		if is_lang(cmd_list[length-2],langslist) and is_lang(cmd_list[length-1],langslist):
			sd.write("%20".join(cmd_list[:length-2]), cmd_list[length-2], cmd_list[length-1])
		else:
			sbserver.playerMessage(cn, red("You've made a mistake with the syntax. Type #trans to show syntax"))

registerCommandHandler('trans', onCommand)
