#coding=utf8
#此脚本须运行在Image的父目录下目录下
#所有写入的文件都不写入后缀名
#要写一个pairlist

import os
import sys
import random
import copy



def writeFile(datasetName, pairNum, databaseNum, fileName, uri):
    if not os.path.exists(os.path.join('Data', datasetName, str(databaseNum), 'pair%s'%pairNum)):
        os.makedirs(os.path.join('Data', datasetName, str(databaseNum), 'pair%s'%pairNum))
    filehandler = open(os.path.join('Data', datasetName, str(databaseNum), 'pair%s' % pairNum, fileName), 'a')
    filehandler.write(uri)
    filehandler.close()

def getRandomNormalPic(picsList):
    normalPicsList = []
    for pic in picsList:
        if '-' in pic:
            normalPicsList.append(pic)
    if len(normalPicsList) == 0:
        return None
    return normalPicsList[random.randint(0, len(normalPicsList) - 1)]

def writePairList(fileName, content):
    filehandler = open(fileName, 'a')
    filehandler.write(content)
    filehandler.close()

try:
    datasetName = sys.argv[1]
    databasePicNum = int(sys.argv[2])
    positiveNum = int(sys.argv[3])
    negativeNum = int(sys.argv[4])
    aorc = sys.argv[5]
except Exception as ep:
    #print ep.message
    print 'wrong arguments: dataset_name database_num positive_num negative_num a(c)'
    sys.exit()

if not os.path.exists(os.path.join('Image', datasetName)):
    print 'cannot find dataset %s' % datasetName
    sys.exit()

#if not os.path.exists(os.path.join('Data', datasetName, str(databasePicNum))):
    #os.makedirs(os.path.join('Data', datasetName, str(databasePicNum)))



allDirsList = os.listdir(os.path.join('Image', datasetName, 'database'))
for eachFile in allDirsList:
    if not os.path.isdir(os.path.join('Image', datasetName, 'database', eachFile)):
        allDirsList.remove(eachFile)

tempDirsList = allDirsList
alreadyPairNum = 1

alreadyPositiveNum = 0
alreadyNegativeNum = 0


# 非证件照也是尽量取多次，而不是把一个人的照片全取了

while 1:
    tempDirsList = copy.copy(allDirsList)

    # for each pair, generate database.txt, positive.txt, negative.txt
    # generate database.txt
    alreadyDatabasePicNum = 0
    selectedPeopleList = []
    while 1:
        selectedFolder = tempDirsList[random.randint(0, len(tempDirsList)-1)]
        tempDirsList.remove(selectedFolder)
        picsList = os.listdir(os.path.join('Image', datasetName, 'database', selectedFolder))
        hasIDPhoto = False

        for eachPic in picsList:
            if eachPic.split('.')[0][-3:] == 'id1' and aorc == 'a':
                hasIDPhoto = True
                picURI = str(os.path.join(datasetName, 'database', selectedFolder, eachPic.split('.')[0]))
                writeFile(datasetName+'_a_newNoise', alreadyPairNum, databasePicNum, 'database.txt', picURI+'\n')
            elif eachPic.split('.')[0][-3:] == 'id2' and aorc == 'c':
                hasIDPhoto = True
                picURI = str(os.path.join(datasetName, 'database', selectedFolder, eachPic.split('.')[0]))
                writeFile(datasetName+'_c_newNoise', alreadyPairNum, databasePicNum, 'database.txt', picURI+'\n')
        

        if hasIDPhoto == True:
            alreadyDatabasePicNum += 1
            selectedPeopleList.append(selectedFolder)
        
        if alreadyDatabasePicNum == databasePicNum:
            break

    #generate positive.txt
    if alreadyPositiveNum < positiveNum:
        tempSelectedPeopleList = copy.copy(selectedPeopleList)
        while 1:
            randomNumber = random.randint(0, len(tempSelectedPeopleList)-1)
            selectedFolder = tempSelectedPeopleList[random.randint(0, randomNumber)]
            tempSelectedPeopleList.remove(selectedFolder)
            picsList = os.listdir(os.path.join('Image', datasetName, 'database', selectedFolder))
            normalPicsList = []
            for eachPic in picsList:
                if eachPic.split('.')[0][-3:] != 'id1' and eachPic.split('.')[0][-3:] != 'id2':
                    normalPicsList.append(eachPic)

            if not len(normalPicsList) == 0:
                selectedPic = normalPicsList[random.randint(0, len(normalPicsList) - 1)]
                picURI = str(os.path.join(datasetName, 'database', selectedFolder, selectedPic.split('.')[0]))
                if aorc == 'a':
                    writeFile(datasetName+'_a_newNoise', alreadyPairNum, databasePicNum, 'positive.txt', picURI+'\n')
                elif aorc == 'c':
                    writeFile(datasetName+'_c_newNoise', alreadyPairNum, databasePicNum, 'positive.txt', picURI+'\n')
                alreadyPositiveNum += 1
            if alreadyPositiveNum == positiveNum or len(tempSelectedPeopleList) == 0:
                break

    # generate negative.txt
    # allNoisePics中也是自带完整路径，且没有后缀名
    if alreadyNegativeNum < negativeNum:
        allNoisePics = []
        tempDirsList = copy.copy(allDirsList)
        for eachFolder in tempDirsList:
            if not eachFolder in selectedPeopleList:
                tempPicsList = os.listdir(os.path.join('Image', datasetName, 'database', eachFolder))
                randomPic = getRandomNormalPic(tempPicsList)
                if randomPic == None:
                    continue
                allNoisePics.append(str(os.path.join(datasetName, 'database', eachFolder, randomPic.split('.')[0])))

        while 1:
            selectedNegativePic = allNoisePics[random.randint(0, len(allNoisePics) - 1)]
            allNoisePics.remove(selectedNegativePic)
            if aorc == 'a':
                writeFile(datasetName+'_a_newNoise', alreadyPairNum, databasePicNum, 'negative.txt', selectedNegativePic+'\n')
            elif aorc == 'c':
                writeFile(datasetName+'_c_newNoise', alreadyPairNum, databasePicNum, 'negative.txt', selectedNegativePic+'\n')                
            alreadyNegativeNum += 1
            if alreadyNegativeNum == negativeNum or len(allNoisePics) == 0:
                break

    if aorc == 'a':
        writePairList(os.path.join('Data', datasetName+'_a_newNoise', str(databasePicNum), 'pairlist.txt'), str(alreadyPairNum)+'\n')
    elif aorc == 'c':
        writePairList(os.path.join('Data', datasetName+'_c_newNoise', str(databasePicNum), 'pairlist.txt'), str(alreadyPairNum)+'\n')
    print 'pair %s has done' % alreadyPairNum
    alreadyPairNum += 1
    if alreadyNegativeNum == negativeNum and alreadyPositiveNum == positiveNum:
        break









