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

def flattenDir(dirName):
	allSubFilesList = os.listdir(dirName)
	for subFile in allSubFilesList:
		shutil.move(os.path.join(dirName, subFile), '.')
	os.rmdir(dirName)

partNum = (len(processDirs)-1) / eachPartNum + 1

for i in range(len(processDirs)):
	if 'part' in processDirs[i]:
		print 'flatening %s now' % processDirs[i]
		flattenDir(processDirs[i])


allDirsInDir = os.listdir('.')
processDirs = []
for eachFile in allDirsInDir:
	if os.path.isdir(eachFile):
		processDirs.append(eachFile)


for i in range(len(processDirs)):
	belongPartName = '%s_part%s' % (prefix, (i/eachPartNum))
	partName = '%s_part%s' % (prefix, (i/eachPartNum))
	if not os.path.exists(partName):
		os.makedirs(partName)
	print 'before move, dirName is %s and partName is %s' % (processDirs[i], partName)
	shutil.move(processDirs[i], partName)