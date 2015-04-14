#coding=utf-8
import random
import os
import sys
import uuid
import shutil


currentDirList = os.listdir('.')
if not 'Xunfei' in currentDirList:
	print 'cannot find xunfei folder'
	sys.exit()




allDataNum = 500000
dataBaseNum = 20000
noiseNum = 100000


if not os.path.exists('Database'):
	os.makedirs('Database')

if not os.path.exists('Noise'):
	os.makedirs('Noise')

allPeopleList = os.listdir('Xunfei')[:allDataNum]
for eachDir in allPeopleList:
	if not os.path.isdir(eachDir):
		allPeopleList.remove(eachDir)


alreadySelectedNum = 0
while 1:
	randomSelectedIndex = random.randint(0, len(allPeopleList)-1)
	selectedFolder = allPeopleList[randomSelectedIndex]
	shutil.copytree(os.path.join('Xunfei', selectedFolder), os.path.join('Database', selectedFolder))
	allPeopleList.remove(selectedFolder)
	alreadySelectedNum += 1
	if alreadySelectedNum == dataBaseNum:
		break

alreadySelectedNum = 0
while 1:
	randomSelectedIndex = random.randint(0, len(allPeopleList)-1)
	selectedFolder = allPeopleList[randomSelectedIndex]
	allPeopleList.remove(selectedFolder)
	picsList = os.listdir(os.path.join('Xunfei', selectedFolder))
	for pic in picsList:
		if not '-' in pic:
			picsList.remove(pic)
			break
	try:
		noisePic = picsList[random.randint(0, len(picsList)-1)]
	except Exception as ep:
		continue

	shutil.copyfile(os.path.join('Xunfei', selectedFolder, noisePic), os.path.join('Noise', noisePic))
	alreadySelectedNum += 1
	if alreadySelectedNum == noiseNum:
		break





