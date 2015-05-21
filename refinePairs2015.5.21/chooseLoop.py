#coding=utf8
import os
import shutil
import copy



setNum = 6
def getListFromFile(fileName):
	fileLines = open(fileName).read().split('\n')
	resultList = []
	for eachLine in fileLines:
		if eachLine == '\n' or eachLine == '' or eachLine == '\r':
			continue
		resultList.append((eachLine.split(' ')[0], eachLine.split(' ')[1]))
	return resultList

resultDict = {}

currentKey = 0
dupList = getListFromFile('dataset%s_dup.txt' % setNum)
for i in range(len(dupList)):
	dupPic1 = dupList[i][0]
	dupPic2 = dupList[i][1]
	didInsert = False
	for eachKey in resultDict.keys():
		keyList = resultDict[eachKey]
		if dupPic1 in keyList and not dupPic2 in keyList:
			resultDict[eachKey].append(dupPic2)
			didInsert = True
		elif not dupPic1 in keyList and dupPic2 in keyList:
			resultDict[eachKey].append(dupPic1)
			didInsert = True
		elif dupPic2 in keyList and dupPic1 in keyList:
			didInsert = True
	if didInsert == False:
		resultDict[currentKey] = []
		resultDict[currentKey].append(dupPic1)
		resultDict[currentKey].append(dupPic2)
		currentKey += 1


filehandler = open('duplicate%s.txt' % setNum, 'w')
for eachKey in resultDict.keys():
	sameList = resultDict[eachKey]
	for eachpic in sameList:
		filehandler.write(eachpic+' ')
	filehandler.write('\n')
filehandler.close()


def getMappingListFromFile(fileName):
	fileLines = open(fileName).read().split('\n')
	resultList = []
	for eachLine in fileLines:
		if eachLine == '\n' or eachLine == '' or eachLine == '\r':
			continue
		resultList.append((eachLine.split(',')[0], eachLine.split(',')[1]))
	return resultList



def getDupListFromFile(fileName):
	fileLines = open(fileName).read().split('\n')
	resultList = []
	for eachLine in fileLines:
		if eachLine == '\n' or eachLine == '' or eachLine == '\r':
			continue
		resultList.append(eachLine.split(' ')[:-1])
	return resultList

resultDict = {}

reservedList = getDupListFromFile('duplicate%s.txt' % setNum)
mappingList = getMappingListFromFile('Mapping_ds%s.csv' % setNum)
newmappingList = copy.copy(mappingList)
for i in range(len(reservedList)):
	sameList = reservedList[i]
	for j in range(1, len(sameList)):

		picPath = os.path.join('dataset%s' % setNum, 'A', sameList[j])
		if not os.path.exists(picPath):
			print 'cannot find pic %s' % picPath
			#continue
		#print 'picPath is %s' % picPath
		else:
			os.remove(picPath)
			print 'A pic %s is deleted' % picPath
		
		for k in range(len(mappingList)):
			#print mappingList[k]
			#print sameList[j]
			if mappingList[k][0] == sameList[j]:
				picPath = os.path.join('dataset%s' % setNum, 'B', mappingList[k][1])
				if not os.path.exists(picPath):
					print 'cannot find pic %s' % picPath
					
				else:
					os.remove(picPath)
				newmappingList.remove(mappingList[k])



filehandler = open('newmapping_ds%s.csv' % setNum, 'w')
for i in range(len(newmappingList)):
	filehandler.write(newmappingList[i][0]+','+ newmappingList[i][1]+'\n')
filehandler.close()

