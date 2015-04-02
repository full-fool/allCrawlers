#coding=utf-8
import os
import shutil
import sys

print 'please input the prefix'
prefix = str(raw_input())

print 'please input folders number in each package'
try:
	eachPartNum = int(raw_input())
except Exception as ep:
	print 'wrong input'
	sys.exit()

allDirsInDir = os.listdir('.')
processDirs = []
for eachFile in allDirsInDir:
	if os.path.isdir(eachFile):
		processDirs.append(eachFile)

partNum = (len(processDirs)-1) / eachPartNum + 1

for i in range(len(processDirs)):
	belongPartName = '%s_part%s' % (prefix, (i/eachPartNum))
	partName = '%s_part%s' % (prefix, (i/eachPartNum))
	if not os.path.exists(partName):
		os.makedirs(partName)
	shutil.move(processDirs[i], partName)