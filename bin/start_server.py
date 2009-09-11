#!/usr/bin/env python
import os, sys

xsbs_root_path = ''
pyscripts_path = ''
xsbs_bin_path = ''

cwddirs = os.getcwd().split('/')
root_found = False

if xsbs_root_path == '':
	for dir in cwddirs:
		if dir == 'xsbs':
			root_found = True
		xsbs_root_path += dir + '/'
else:
	root_found = True

if not root_found:
	print 'Error: Could not find XSBS root in your current path.'
	print 'Please cd into the XSBS source directory and re-run this script.'
	sys.exit(1)

if pyscripts_path == '':
	pyscripts_path = xsbs_root_path + 'src/pyscripts'
if not os.path.isdir(pyscripts_path):
	print 'Error: Could not find pyscripts folder in your XSBS directory.'
	print 'Did you perform an out of source build?  Make sure you are in the XSBS source directory.'
	sys.exit(1)

if xsbs_bin_path == '':
	xsbs_bin_path = xsbs_root_path + 'src/xsbs'
if not os.path.isfile(xsbs_bin_path):
	os.execlpe('xsbs', 'xsbs', '-lsauer.log', '-s'+pyscripts_path, os.environ)
else:
	os.execle(xsbs_bin_path, '-lsauer.log', '-s'+pyscripts_path, os.environ)

