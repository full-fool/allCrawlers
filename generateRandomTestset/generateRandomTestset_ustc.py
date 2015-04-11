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


if os.path.exists('official'):
	shutil.rmtree('official')
os.makedirs('official')

if os.path.exists('normal'):
	shutil.rmtree('normal')
os.makedirs('normal')

if os.path.exists('Mapping.csv'):
	os.remove('Mapping.csv')
	
allNamesListOri = os.listdir('Image')
allNamesList = []
for oriFile in allNamesListOri:
	if os.path.isdir(os.path.join('Image', oriFile)):
		allNamesList.append(oriFile)

totalNum = len(allNamesList)

for i in range(totalNum):
	randomFolderIndex = random.randint(0, totalNum - 1)
	randomFolderName = allNamesList[randomFolderIndex]
	#print randomFolderName
	picsList = os.listdir(os.path.join('Image', randomFolderName))
	normalPicsList = []
	newNameOfficial = None
	officialPicsList = []
	for pics in picsList:
		if '_i_01_00_00_HP_00' in pics:
			officialPicsList.append(pics)
			newNameOfficial = genUUID() + '.' + pics.split('.')[1]
			shutil.copyfile(os.path.join('Image', randomFolderName, pics), os.path.join('official', newNameOfficial))
		else:
			normalPicsList.append(pics)


	#print len(officialPicsList), randomFolderName
	for j in range(4):
		randomNormalPicsName = normalPicsList[random.randint(0, len(normalPicsList)-1)]
		newNameNormal = genUUID() + '.' + randomNormalPicsName.split('.')[1]
		shutil.copyfile(os.path.join('Image', randomFolderName, randomNormalPicsName), os.path.join('normal', newNameNormal))
		writeMapping(newNameOfficial+','+newNameNormal+'\n')
		normalPicsList.remove(randomNormalPicsName)

	allNamesList.remove(randomFolderName)
	totalNum -= 1
