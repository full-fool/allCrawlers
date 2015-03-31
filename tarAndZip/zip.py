#coding=utf-8

import os
import shutil
from zipfile import *
import zipfile
import threading




class ZipFile(threading.Thread):
	def __init__(self, dirName):
		threading.Thread.__init__(self)
		self.dirName = dirName

	def run(self):
		dirName = self.dirName
		f = zipfile.ZipFile('%s.zip' % dirName,'w',zipfile.ZIP_STORED)   
		startdir = dirName
		for dirpath, dirnames, filenames in os.walk(startdir):    
			for filename in filenames:    
				f.write(os.path.join(dirpath,filename))    
		f.close()
		print 'dirName has been done'



for eachDir in os.listdir('.'):
	if not os.path.isdir(eachDir):
		continue
	ZipFile(eachDir).start()





