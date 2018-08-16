#!dep/bin/python

import os, sys, subprocess, shutil, json

def build():
	path = subprocess.check_output("pwd" , shell=True).strip()

	original = path + "/python/treeTemplates/home.html"
	openFile = open(original).read()
	j = json.loads(sys.stdin.readline())
	mappArray = j["mappArray"]

	for key, value in mappArray.iteritems():
		if value == "1":
			openFile = openFile.replace(key+'" style="display:none;"', key+'" style="display:;"')

	authentic = path + "/python/public/templates/home.html"
	f = open(authentic, 'w')
	f.write(openFile)
	f.close()
	return
	

	
if __name__=='__main__':
	build()
