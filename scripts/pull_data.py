# Receive 'Exception: Unable to parse token: <!DOCTYPE' error when using pydap.

'''from pydap.client import open_url
url = "http://oceanparcels.org/examples-data/OFAM_example_data"#/OAFM_simple_U.nc"
OAFM_simple_U = open_url(url)'''

import urllib2
import os
from datetime import date, datetime, timedelta

def import_MovingEddies_example():
	url = "http://oceanparcels.org/examples-data/MovingEddies_data"
	filenames = ["moving_eddiesP.nc", "moving_eddiesU.nc", "moving_eddiesV.nc"]
	path = "examples/MovingEddies_data"
	if not os.path.exists(path):
		os.makedirs(path)

	filecount = 0
	for filename in filenames:
		filecount += 1
		if not os.path.exists(os.path.join(path,filename)):
			f = urllib2.urlopen(url + "/" + filename)
			print "Downloading %s; file %i of %i" % (filename, filecount, len(filenames))
			with open(os.path.join(path, filename), 'wb') as temp_file:
				temp_file.write(f.read())
			print "%s written to %s" % (filename, path)
		else:
			print "%s already exists within %s" % (filename, path)

def import_globcurrent_example():
	url = "http://oceanparcels.org/examples-data/GlobCurrent_example_data"
	filenames = []
	dt = datetime(2002, 01, 01)
	end = datetime(2003, 01, 01)
	step = timedelta(days = 1)
	while dt < end:
		filenames.append(dt.strftime("%Y%m%d") + "000000-GLOBCURRENT-L4-CUReul_hs-ALT_SUM-v02.0-fv01.0.nc")
		dt += step
	path = "examples/GlobCurrent_example_data"
	
	if not os.path.exists(path):
		os.makedirs(path)

	filecount = 0
	for filename in filenames:
		filecount += 1
		if not os.path.exists(os.path.join(path,filename)):
			f = urllib2.urlopen(url + "/" + filename)
			print "Downloading %s; file %i of %i" % (filename, filecount, len(filenames))
			with open(os.path.join(path, filename), 'wb') as temp_file:
				temp_file.write(f.read())
			print "%s written to %s" % (filename, path)
		else:
			print "%s already exists within %s" % (filename, path)

def import_OFAM_example():
	url = "http://oceanparcels.org/examples-data/OFAM_example_data"
	filenames = ["OFAM_simple_U.nc", "OFAM_simple_V.nc"]
	path = "examples/OFAM_example_data"
	
	if not os.path.exists(path):
		os.makedirs(path)

	filecount = 0
	for filename in filenames:
		filecount += 1
		if not os.path.exists(os.path.join(path,filename)):
			f = urllib2.urlopen(url + "/" + filename)
			print "Downloading %s; file %i of %i" % (filename, filecount, len(filenames))
			with open(os.path.join(path, filename), 'wb') as temp_file:
				temp_file.write(f.read())
			print "%s written to %s" % (filename, path)
		else:
			print "%s already exists within %s" % (filename, path)


if __name__ == "__main__":
	import_MovingEddies_example()
	import_globcurrent_example()
	import_OFAM_example()
