import os
from xsbs.server import csevalfile

path = "cubescript"

if os.path.exists(path):
	files = os.listdir(path)
	for file in files:
		if file[0] != '.' and file != '..':
			csevalfile(os.path.join(path, file))