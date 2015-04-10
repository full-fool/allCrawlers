#coding=utf-8
import random
import os
import sys
import uuid
import shutil


def writeMapping(content):
	filehandler = open('Mapping.csv', 'a')
	filehandler.write(content+'\n')
	filehandler.close()

requiredPairsNum = 500



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

for i in range(requiredPairsNum):
	randomFolderIndex = random.randint(0, totalNum - 1)
	randomFolderName = allNamesList[randomFolderIndex]
	print randomFolderName
	picsList = os.listdir(os.path.join('Image', randomFolderName))
	normalPicsList = []
	newNameOfficial = None
	for pics in picsList:
		if not '-' in pics:
			newNameOfficial = str(uuid.uuid1()) + '.' + pics.split('.')[1]
			shutil.copyfile(os.path.join('Image', randomFolderName, pics), os.path.join('official', newNameOfficial))
		else:
			normalPicsList.append(pics)

	randomNormalPicsName = normalPicsList[random.randint(0, len(normalPicsList)-1)]
	newNameNormal = str(uuid.uuid1()) + '.' + randomNormalPicsName.split('.')[1]
	shutil.copyfile(os.path.join('Image', randomFolderName, randomNormalPicsName), os.path.join('normal', newNameNormal))
	writeMapping(newNameOfficial+','+newNameNormal)

	allNamesList.remove(randomFolderName)
	totalNum -= 1
