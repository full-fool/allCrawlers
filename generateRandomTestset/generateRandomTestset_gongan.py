#coding=utf-8
import random
import os
import sys
import uuid
import shutil


def writeMapping(content):
	filehandler = open('Mapping_Gongan.csv', 'a')
	filehandler.write(content)
	filehandler.close()




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

requiredNum = 250


if os.path.exists('official'):
	shutil.rmtree('official')
os.makedirs('official')

if os.path.exists('normal'):
	shutil.rmtree('normal')
os.makedirs('normal')

if os.path.exists('Mapping_Gongan.csv'):
	os.remove('Mapping_Gongan.csv')
	
allNamesListOri = os.listdir('.')
allNamesList = []
for oriFile in allNamesListOri:
	if 'jpg' in oriFile:
		allNamesList.append(oriFile)

peoplePicsDict = {}
for eachPic in allNamesList:
	if not peoplePicsDict.has_key(eachPic.split('-')[0]):
		peoplePicsDict[eachPic.split('-')[0]] = []
		peoplePicsDict[eachPic.split('-')[0]].append(eachPic)
	else:
		peoplePicsDict[eachPic.split('-')[0]].append(eachPic)

alreadyPickedPeople = 0
while 1:
	randPersonIndex = random.randint(0, len(peoplePicsDict.keys())-1)
	peopleNameKey = peoplePicsDict.keys()[randPersonIndex]
	peoplePicsList = peoplePicsDict[peopleNameKey]
	del peoplePicsDict[peopleNameKey]
	normalPicsNum = 0
	normalPicsList = []
	officialPicsNum = 0
	officialPicsList = []
	for eachPic in peoplePicsList:
		if int(eachPic.split('-')[1].split('.')[0]) > 30:
			officialPicsNum += 1
			officialPicsList.append(eachPic)
		else:
			normalPicsNum += 1
			normalPicsList.append(eachPic)
	if normalPicsNum < 2 or officialPicsNum < 2:
		continue
	firstNormalPic = normalPicsList[random.randint(0, len(normalPicsList)-1)]

	newFirstNormalPicName = genUUID() + '.' + firstNormalPic.split('.')[1]
	normalPicsList.remove(firstNormalPic)
	secondNormalPic = normalPicsList[random.randint(0, len(normalPicsList)-1)]
	newSecondNormalPicName = genUUID() + '.' + secondNormalPic.split('.')[1]
	shutil.copyfile(firstNormalPic, os.path.join('normal', newFirstNormalPicName))
	shutil.copyfile(secondNormalPic, os.path.join('normal', newSecondNormalPicName))




	firstOfficialPic = officialPicsList[random.randint(0, len(officialPicsList)-1)]
	newFirstOfficialPicName = genUUID() + '.' + firstOfficialPic.split('.')[1]
	officialPicsList.remove(firstOfficialPic)
	secondOfficialPic = officialPicsList[random.randint(0, len(officialPicsList) - 1)]
	newSecondOfficialPicName = genUUID() + '.' + secondOfficialPic.split('.')[1]
	shutil.copyfile(firstOfficialPic, os.path.join('official', newFirstOfficialPicName))
	shutil.copyfile(secondOfficialPic, os.path.join('official', newSecondOfficialPicName))

	writeMapping('%s,%s\n%s,%s\n%s,%s\n%s,%s\n' % (newFirstNormalPicName, newFirstOfficialPicName, newFirstNormalPicName,\
	 newSecondOfficialPicName, newSecondNormalPicName, newFirstOfficialPicName, newSecondNormalPicName, newSecondOfficialPicName))

	
	alreadyPickedPeople += 1
	if alreadyPickedPeople == requiredNum:
		break
sys.exit()






for eachPeople in peoplePicsDict.keys():
	peoplePicsList = peoplePicsDict[eachPeople]
	normalPicsNum = 0
	officialPicsNum = 0
	for eachPic in peoplePicsList:
		if int(eachPic.split('-')[1].split('.')[0]) > 30:
			officialPicsNum += 1
		else:
			normalPicsNum += 1
	if normalPicsNum < 2 or officialPicsNum < 2:
		del peoplePicsDict[eachPeople]
print len(peoplePicsDict)
