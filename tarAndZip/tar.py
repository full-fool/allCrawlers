import os
import shutil

eachPartNum = 150
allDirsInDir = os.listdir('.')
processDirs = []
for eachFile in allDirsInDir:
	if os.path.isdir(eachFile):
		processDirs.append(eachFile)

partNum = (len(processDirs)-1) / eachPartNum + 1

for i in range(len(processDirs)):
	belongPartName = 'huafen_part%s' % (i/eachPartNum)
	partName = 'huafen_part%s' % (i/eachPartNum)
	if not os.path.exists(partName):
		os.makedirs(partName)
	shutil.move(processDirs[i], partName)