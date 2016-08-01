# Receive 'Exception: Unable to parse token: <!DOCTYPE' error when using pydap.

'''from pydap.client import open_url
url = "http://oceanparcels.org/examples-data/OFAM_example_data"#/OAFM_simple_U.nc"
OAFM_simple_U = open_url(url)'''

import urllib2
import os

def import_OAFM_example():
	url = "http://oceanparcels.org/examples-data/OFAM_example_data"
	#OAFM_simple_U = urllib2.urlopen(url)
	#html = OAFM_simple_U.read()
	filenames = ["OFAM_simple_U.nc", "OFAM_simple_V.nc"]
	path = "examples/OFAM_example_data"
	if not os.path.exists(path):
		os.makedirs(path)
	for filename in filenames:
		if not os.path.exists(os.path.join(path,filename)):
			with open(os.path.join(path, filename), 'wb') as temp_file:
				temp_file.write(path)
			print "%s written to %s" % (filename, path)
		else:
			print "%s already exists within %s" % (filename, path)

def import_MovingEddies_example():
	url = "oceanparcels.org/examples-data/MovingEddies_data"
	filenames = ["moving_eddiesP.nc", "moving_eddiesU.nc", "moving_eddiesV.nc"]
	path = "examples/MovingEddies_data"
	if not os.path.exists(path):
		os.makedirs(path)
	for filename in filenames:
		if not os.path.exists(os.path.join(path,filename)):
			with open(os.path.join(path, filename), 'wb') as temp_file:
				temp_file.write(path)
			print "%s written to %s" % (filename, path)
		else:
			print "%s already exists within %s" % (filename, path)

if __name__ == "__main__":
	import_OAFM_example()
	import_MovingEddies_example()
