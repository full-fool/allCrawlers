#coding=utf-8
import random
import os
import sys
import uuid
import shutil


def writeFile(fileName, content):
	filehandler = open(fileName, 'a')
	filehandler.write(content)
	filehandler.close()

requiredNum = 500
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

def generateRandomTest(firstFolder, secondFolder, mappingName):
	if os.path.exists(firstFolder):
		shutil.rmtree(firstFolder)
	os.makedirs(firstFolder)

	if os.path.exists(secondFolder):
		shutil.rmtree(secondFolder)
	os.makedirs(secondFolder)

	if os.path.exists(mappingName):
		os.remove(mappingName)
		
	allNamesListOri = os.listdir('Image')

	allNamesList = []
	for oriFile in allNamesListOri:
		if os.path.isdir(os.path.join('Image', oriFile)):
			allNamesList.append(oriFile)


	totalNum = len(allNamesList)


	if requiredNum > totalNum:
		print 'no enough folders, there are %s folders, %s are needed' % (totalNum, requiredNum)
		sys.exit()

	alreadyPeopleNum = 0
	while 1:
		if totalNum < 1:
			print 'no enough folders now, already choose %s folder, \
			there are %s folders left, %s needed in all' % \
			(alreadyPeopleNum, totalNum, requiredNum)
			sys.exit()
		randomFolderIndex = random.randint(0, totalNum - 1)
		randomFolderName = allNamesList[randomFolderIndex]
		allNamesList.remove(randomFolderName)
		totalNum -= 1
		#print randomFolderName
		picsList = os.listdir(os.path.join('Image', randomFolderName))
		firstPic = None
		secondPic = None
		for eachPic in picsList:
			if '-a' in eachPic:
				firstPic = eachPic
			if '-c' in eachPic:
				secondPic = eachPic
		if firstPic == None or secondPic == None:
			print 'no enough pics for ac in people,%s' % randomFolderName
			continue
		
		newFirstName = genUUID() + '.' + firstPic.split('.')[1]
		shutil.copyfile(os.path.join('Image', randomFolderName, firstPic), os.path.join(firstFolder, newFirstName))
		newSecondName = genUUID() + '.' + secondPic.split('.')[1]
		shutil.copyfile(os.path.join('Image', randomFolderName, secondPic), os.path.join(secondFolder, newSecondName))
		writeFile(mappingName, '%s,%s\n'%(newFirstName, newSecondName))
		alreadyPeopleNum += 1
		if alreadyPeopleNum == requiredNum:
			break


generateRandomTest('ac_a', 'ac_c', 'mapping_ac.csv')