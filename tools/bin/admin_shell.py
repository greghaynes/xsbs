#!/usr/bin/env python
import sys, urllib, urllib2

HOST = None
PORT = 8081

if len(sys.argv) < 2:
	print "usage: %s HOST [PORT]" % sys.argv[0]
	sys.exit(1)

HOST = sys.argv[1]

if len(sys.argv) == 3:
	try:
		PORT = int(sys.argv[2])
	except:
		print "malformed port (%s)" % sys.argv[2]
		sys.exit(2)

BASE_URL = "http://%s:%d/" % (HOST, PORT)

def parse_args(s):
	args = []
	acc  = ""
	in_string = False

	for c in s:
		if in_string and c == '"':
			in_string = False
			args.append(acc)
			acc = ""
			continue
		if not in_string and c == '"':
			in_string = True
			continue
		if in_string:
			acc += c
			continue
		if c == ' ':
			args.append(acc)
			acc = ""
			continue

		acc += c

	if acc != "":
		args.append(acc)

	return args

def dourl(url):
	try:
		resp = urllib2.urlopen(url).read()
		return resp
	except urllib2.HTTPError, e:
		print "http error code %d: %s" % (e.code, e.reason)
	except urllib2.URLError, e:
		print "error sending request: %s" % e.reason

def eval_command(args):
	cmd = args[0]

	if cmd == "config_set":
		plugin  = urllib.quote(args[1])
		section = urllib.quote(args[2])
		option  = urllib.quote(args[3])
		value   = urllib.quote(args[4])

		resp = dourl(BASE_URL + "json/config/%s/%s/%s?set=%s" % (plugin, section, option, value))

		# todo: parse output
	elif cmd == "quit" or cmd == "exit" or cmd == "bye":
		print "bye"
		sys.exit(0)
	else:
		print "unknown command \"%s\"" % cmd

# repl
while True:
	try:
		args = parse_args(raw_input("> "))
	except:
		print "bye"
		break

	eval_command(args)
