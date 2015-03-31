import os
import shutil
from zipfile import *
import zipfile


partNum = 0
for eachDir in os.listdir('.'):
	if not os.path.isdir(eachDir):
		continue
	f = zipfile.ZipFile('%s.zip' % eachDir,'w',zipfile.ZIP_STORED)   
	partNum += 1 	
	startdir = eachDir
	for dirpath, dirnames, filenames in os.walk(startdir):    
	    for filename in filenames:    
	        f.write(os.path.join(dirpath,filename))    
	f.close()

