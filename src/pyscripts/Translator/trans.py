import sbserver
from xsbs.commands import registerCommandHandler
from xsbs.settings import PluginConfig
from xsbs.colors import red, green, white
import socket, re, asyncore

cmd_name = 'translate'
fault_message = "Usage: #%s <word> or #%s <sentence/word> <from_lang> <to_lang> Language codes: en, sv, de, it and lots more." % (cmd_name, cmd_name)

player_fd_limit = 10

config = PluginConfig(cmd_name)
from_lang = config.getOption('Config', 'from_lang', 'en')
to_lang = config.getOption('Config', 'to_lang', 'sv')
del config

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

url = 'http://%s/ajax/services/language/translate' % host
header = 'GET %s?langpair=%s|%s&v=1.0&q=%s HTTP/1.0\r\n\r\n'

begin = 'translatedText\":\"'
end = '\"'
pattern = re.compile(begin+"(.*?)"+end, re.DOTALL)

socket_dispatchers = {}#k: cn, v: list of sd's handling translation requests
class SocketDispatch(asyncore.dispatcher):
	def __init__(self, host, port, header, url, pattern, cn):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.url = url
		self.host = host
		self.port = port
		self.setblocking(0)
		self.buff = ''
		self.writebuff = ''
		self.header = header
		self.pattern = pattern
		self.cn = cn
		self.connect((self.host, self.port))
	def __del__(self):
		self.close()
	def handle_connect(self):
		pass
	def handle_close(self):
		remove_request(self.cn, self)
	def handle_write(self):
		sent = self.send(self.writebuff)
		self.writebuff = self.writebuff[sent:]
	def handle_read(self):
		self.buff += self.recv(4096)
		if self.buff != "":
			m = re.search(self.pattern, self.buff)
			self.buff = ""
			sbserver.playerMessage(self.cn, green('Translation: ') + white(m.group(1)))
		remove_request(self.cn, self)
	def write(self,query, from_lang, to_lang):
		self.writebuff += self.header % (self.url, from_lang, to_lang, query)

def remove_request(cn, sd):
	removeindex = -1
	for index,request in enumerate(socket_dispatchers[cn]):
		if request is sd:
			removeindex = index
	if removeindex >= 0:
		del socket_dispatchers[cn][removeindex]
	
def add_request(cn, sd):
	try:
		socket_dispatchers[cn].append(sd)
	except Exception:
		socket_dispatchers[cn] = [sd]
		
def count_player_requests(cn):
	try:
		return len(socket_dispatchers[cn])
	except KeyError:
		return 0

def is_lang(s,langs):
	for lang in langs:
		if lang.lower() == s.lower():
			return True
	return False

def onCommand(cn, command):
	'''@description Translate text using Google translator
	   @usage text src_lang dest_lang
	   @public'''
	if count_player_requests(cn) < player_fd_limit:
		cmd_list = command.split()
		length = len(cmd_list)
		query = None
		lang1 = from_lang
		lang2 = to_lang
		if length == 0:
			sbserver.playerMessage(cn, red(fault_message))
		elif length == 1:
			query = cmd_list[0]
		elif length == 2:
			sbserver.playerMessage(cn, red(fault_message))
		elif length > 2:
			if is_lang(cmd_list[length-2],langslist) and is_lang(cmd_list[length-1],langslist):
				query = "%20".join(cmd_list[:length-2])
				lang1 = cmd_list[length-2]
				lang2 = cmd_list[length-1]
			else:
				sbserver.playerMessage(cn, red(fault_message))
		if query:
			sd = SocketDispatch(host, port, header, url, pattern, cn)
			sd.write(query, lang1, lang2)
			add_request(cn, sd)
	else:
		sbserver.playerMessage(cn, red("Please wait for your translations to be handled before submitting new ones"))

registerCommandHandler(cmd_name, onCommand)
