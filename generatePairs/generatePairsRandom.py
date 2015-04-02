#coding=utf-8
import random
import os
import sys



allNamesList = os.listdir('Image')
selectedNum = len(allNamesList)


print 'input the postive pairs number'
try:
	posPairNum = int(raw_input())
except Exception as ep:
	print 'input error'
	sys.exit()

print 'input the negative pairs number'
try:
	negPairNum = int(raw_input())
except Exception as ep:
	print 'input error'
	sys.exit()

if os.path.exists('pos_result.csv'):
	os.remove('pos_result.csv')
if os.path.exists('neg_result.csv'):
	os.remove('neg_result.csv')
#posPairNum = selectedNum
#negPairNum = 4 * selectedNum

def initializeNotChosenList():
	global selectedNum
	notChosenList = []
	for i in range(selectedNum):
		notChosenList.append(i)
	return notChosenList

def generatePosTestList(pairNum):
	global notChosenList, allNamesList
	alreadyPariNum = 0
	#for i in range(pairNum):
	while 1:
		leftForChooseNum = len(notChosenList)
		randomChosenNum = random.randint(0, leftForChooseNum-1)
		selectedPersonFolder = allNamesList[notChosenList[randomChosenNum]]
		picsOfOnePersonList = os.listdir(os.path.join('Image', selectedPersonFolder))
		picsNumForPerson = len(picsOfOnePersonList)
		if picsNumForPerson >= 2:
			firstPic = picsOfOnePersonList[random.randint(0, picsNumForPerson-1)]
			#firstPic = selectedPersonFolder+'-a.jpg'
			picsOfOnePersonList.remove(firstPic)
			secondPic = picsOfOnePersonList[random.randint(0, picsNumForPerson-2)]


			filehandler = open('pos_result.csv', 'a')
			filehandler.write(selectedPersonFolder+'\\'+firstPic+','+selectedPersonFolder+'\\'+secondPic+',\n')
			filehandler.close()
			alreadyPariNum += 1
		if alreadyPariNum >= pairNum:
			break
		
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


		firstPersonPicList = os.listdir(os.path.join('Image', allNamesList[firstPersonNum]))
		secondPersonPicList = os.listdir(os.path.join('Image', allNamesList[secondPersonNum]))

		firstPic = firstPersonPicList[random.randint(0, len(firstPersonPicList)-1)]
		secondPic = secondPersonPicList[random.randint(0, len(secondPersonPicList)-1)]



		filehandler = open('neg_result.csv', 'a')
		filehandler.write(allNamesList[firstPersonNum]+'\\' + firstPic +  ',' + allNamesList[secondPersonNum] + '\\'+ secondPic +',\n')
		filehandler.close()


notChosenList = initializeNotChosenList()
generatePosTestList(posPairNum)
notChosenList = initializeNotChosenList()
generateNegTestList(negPairNum)

