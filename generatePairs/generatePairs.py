#coding=utf-8
import random
import os
import sys



allNamesList = os.listdir('Image')
selectedNum = len(allNamesList)

posPairNum = selectedNum
negPairNum = 4 * selectedNum

def initializeNotChosenList():
	global selectedNum
	notChosenList = []
	for i in range(selectedNum):
		notChosenList.append(i)
	return notChosenList

def generatePosTestList(pairNum):
	global notChosenList, allNamesList
	for i in range(pairNum):
		leftForChooseNum = len(notChosenList)
		randomChosenNum = random.randint(0, leftForChooseNum-1)
		selectedPersonFolder = allNamesList[notChosenList[randomChosenNum]]
		picsOfOnePersonList = os.listdir('Image\\' + selectedPersonFolder)
		firstPic = selectedPersonFolder+'-a.jpg'
		secondPic = selectedPersonFolder+'-b.jpg'
		thirdPic = selectedPersonFolder+'-c.jpg'
		if not (firstPic in picsOfOnePersonList and secondPic in picsOfOnePersonList and thirdPic in picsOfOnePersonList):
			print 'something wrong in %s, maybe it is empty'% selectedPersonFolder
			sys.exit()

		filehandler = open('pos_result_ab.csv', 'a')
		filehandler.write(selectedPersonFolder+'\\'+firstPic+','+selectedPersonFolder+'\\'+secondPic+',\n')
		filehandler.close()

		filehandler = open('pos_result_ac.csv', 'a')
		filehandler.write(selectedPersonFolder+'\\'+firstPic+','+selectedPersonFolder+'\\'+thirdPic+',\n')
		filehandler.close()

		filehandler = open('pos_result_bc.csv', 'a')
		filehandler.write(selectedPersonFolder+'\\'+secondPic+','+selectedPersonFolder+'\\'+thirdPic+',\n')
		filehandler.close()
		
		notChosenList.remove(notChosenList[randomChosenNum])
		if len(notChosenList) == 0:
			notChosenList = initializeNotChosenList()


def generateNegTestList(pairNum):
	global notChosenList, allNamesList
	for i in range(pairNum):
		leftForChooseNum = len(notChosenList)
		firstPersonNum = notChosenList[random.randint(0, leftForChooseNum-1)] 
		notChosenList.remove(firstPersonNum)
		secondPersonNum = notChosenList[random.randint(0, leftForChooseNum-2)]
		notChosenList.remove(secondPersonNum)
		if len(notChosenList) == 0 or len(notChosenList) == 1:
			notChosenList = initializeNotChosenList()
		firstPic = allNamesList[firstPersonNum]+'-a.jpg'
		secondPic = allNamesList[secondPersonNum]+'-b.jpg'
		thirdPic = allNamesList[secondPersonNum]+'-c.jpg'
		fourthPic = allNamesList[firstPersonNum] + '-b.jpg'
		allPicsOfFirstPerson = os.listdir('Image\\' + allNamesList[firstPersonNum])
		allPicsOfSecondPerson = os.listdir('Image\\' + allNamesList[secondPersonNum])
		if not (firstPic in allPicsOfFirstPerson and fourthPic in allPicsOfFirstPerson):
			print 'something wrong in %s, maybe it is empty' % allNamesList[firstPersonNum]
			sys.exit()
		if not (secondPic in allPicsOfSecondPerson and thirdPic in allPicsOfSecondPerson):
			print 'something wrong in %s, maybe it is empty ' % allNamesList[secondPersonNum]
			sys.exit()

		filehandler = open('neg_result_ab.csv', 'a')
		filehandler.write(allNamesList[firstPersonNum]+'\\' + firstPic +  ',' + allNamesList[secondPersonNum] + '\\'+ secondPic +',\n')
		filehandler.close()

		filehandler = open('neg_result_ac.csv', 'a')
		filehandler.write(allNamesList[firstPersonNum]+'\\' + firstPic +  ',' + allNamesList[secondPersonNum] + '\\'+ thirdPic +',\n')
		filehandler.close()		

		filehandler = open('neg_result_bc.csv', 'a')
		filehandler.write(allNamesList[firstPersonNum]+'\\' + fourthPic +  ',' + allNamesList[secondPersonNum] + '\\'+ thirdPic +',\n')
		filehandler.close()	

notChosenList = initializeNotChosenList()
generatePosTestList(posPairNum)
notChosenList = initializeNotChosenList()
generateNegTestList(negPairNum)

