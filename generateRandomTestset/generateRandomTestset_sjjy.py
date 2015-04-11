#coding=utf-8
import random
import os
import sys
import uuid
import shutil


def writeMapping(content):
	filehandler = open('Mapping.csv', 'a')
	filehandler.write(content)
	filehandler.close()

requiredPairsNum = 500
uuidList = []

def genUUID():
	global uuidList
	newUUID = None
	while 1:
		newUUID = uuid.uuid4()
		if not str(newUUID) in uuidList:
			uuidList.append(str(newUUID))
			break
	return str(newUUID)


if os.path.exists('partA'):
	shutil.rmtree('partA')
os.makedirs('partA')

if os.path.exists('partB'):
	shutil.rmtree('partB')
os.makedirs('partB')

if os.path.exists('Mapping.csv'):
	os.remove('Mapping.csv')
	
allNamesListOri = os.listdir('Image')
allNamesList = []
for oriFile in allNamesListOri:
	if os.path.isdir(os.path.join('Image', oriFile)):
		allNamesList.append(oriFile)

totalNum = len(allNamesList)

alreadyPeopleNum = 0
while 1:
	randomFolderIndex = random.randint(0, totalNum - 1)
	randomFolderName = allNamesList[randomFolderIndex]
	#print randomFolderName
	picsList = os.listdir(os.path.join('Image', randomFolderName))
	if len(picsList) < 2:
		continue
	firstPic = picsList[random.randint(0, len(picsList)-1)]

	newFirstPic = genUUID() + '.' + firstPic.split('.')[1]
	picsList.remove(firstPic)
	secondPic = picsList[random.randint(0, len(picsList)-1)]

	newSecondPic = genUUID() + '.' + secondPic.split('.')[1]
	
	shutil.copyfile(os.path.join('Image', randomFolderName, firstPic), os.path.join('partA', newFirstPic))
	shutil.copyfile(os.path.join('Image', randomFolderName, secondPic), os.path.join('partB', newSecondPic))
	writeMapping(newFirstPic+','+newSecondPic+'\n')
	alreadyPeopleNum += 1
	if alreadyPeopleNum == requiredPairsNum:
		break



