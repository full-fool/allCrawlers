#coding=utf-8

import os
import shutil
from zipfile import *
import zipfile
import threading
import sys




class ZipDir(threading.Thread):
	def __init__(self, dirName):
		threading.Thread.__init__(self)
		self.dirName = dirName

	def run(self):

		dirName = self.dirName
		#print 'dirName is %s' % dirName
		if os.path.exists('%s.zip' % dirName):
			print '%s.zip has already exist\n' 
			return
		f = zipfile.ZipFile('%s.zip' % dirName,'w',zipfile.ZIP_STORED, allowZip64=True)  
		startdir = dirName
		for dirpath, dirnames, filenames in os.walk(startdir):    
			for filename in filenames:    
				f.write(os.path.join(dirpath,filename))    
		f.close()
		print '%s has been done' % dirName




DirList = []
OriList = os.listdir('.')
for eachFile in OriList:
	if os.path.isdir(eachFile):
		DirList.append(eachFile)

for eachDir in DirList:
	if not os.path.isdir(eachDir):
		continue
	ZipDir(eachDir).start()





