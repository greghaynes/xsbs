import irclib
import os, sys, time
import threading
import getopt

_win = (sys.platform == 'win32')

class FileMonitor(threading.Thread):
    def __init__(self, file, lock):
        threading.Thread.__init__(self)
        self.daemon = True
        self.mtimes = {}
        self.file = file
        self.lock = lock
        self.queue = []
    def run(self):
        print 'running'
        while True:
            self._scan()
            time.sleep(1)
    def _scan(self):
		filename = self.file
		# stat() the file.  This might fail if the module is part of a
		# bundle (.egg).  We simply skip those modules because they're
		# not really reloadable anyway.
		try:
			stat = os.stat(filename)
		except OSError:
			return
		# Check the modification time.  We need to adjust on Windows.
		mtime = stat.st_mtime
		if _win:
			mtime -= stat.st_ctime
		# If this is a new file, just register its mtime and move on.
		if filename not in self.mtimes:
			self.mtimes[filename] = mtime
			return
		# If this file's mtime has changed, queue it for reload.
		if mtime != self.mtimes[filename]:
			print 'modified'
			self.lock.acquire()
			self.queue.append(filename)
			self.lock.release()
			self.mtimes[filename] = mtime

def onWelcome(server, event):
	server.join('#xsbs')

def main(logfile):
	f = open(logfile, 'r')
	f.seek(os.SEEK_END)
	irc = irclib.IRC()
	server = irc.server()
	lock = threading.Lock()
	mon = FileMonitor(logfile, lock)
	mon.start()
	server.add_global_handler('welcome', onWelcome)
	server.connect('irc.gamesurge.net', 6667, 'xsbs-serverbot')
	while 1:
		if len(mon.queue) > 0:
			lock.acquire()
			buff = f.read(4096)
			lines = buff.split('\n')
			for line in lines:
					server.privmsg('#xsbs', line)
			del mon.queue[:]
			lock.release()
		irc.process_once(timeout=.4)

def help():
	print 'XSBS Server IRC Bot'
	print 'usage python ircbot.py --logfile /path/to/server.log'
	
if __name__ == "__main__":
	opts, args = getopt.getopt(sys.argv[1:], 'hl', ['help', 'logfile='])
	logfile = ''
	print opts, args
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			help()
		elif opt in ('-l', '--logfile'):
			logfile = arg
	if logfile != '':
		main(logfile)
	else:
		help()