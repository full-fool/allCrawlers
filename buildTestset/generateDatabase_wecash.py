#coding=utf-8
import random
import os
import sys
import uuid
import shutil


try:
    datasetPath = sys.argv[1]
    targetPath = sys.argv[2]
except Exception as ep:
    print 'wrong argument, datasetPath targetPath'
    sys.exit()

if not os.path.exists(datasetPath):
    print 'cannot find dataset'
    sys.exit()







os.chdir(targetPath)

if not os.path.exists('database'):
    os.makedirs('database')


allPeopleList = os.listdir(datasetPath)
for eachDir in allPeopleList:
    if not os.path.isdir(os.path.join(datasetPath, eachDir)):
        allPeopleList.remove(eachDir)


# Database
while 1:
    randomSelectedIndex = random.randint(0, len(allPeopleList)-1)
    selectedFolder = allPeopleList[randomSelectedIndex]
    allPeopleList.remove(selectedFolder)
    if len(os.listdir(os.path.join(datasetPath, selectedFolder))) == 3:
        shutil.copytree(os.path.join(datasetPath, selectedFolder), os.path.join('database', selectedFolder))
        newPicsList = os.listdir(os.path.join('database', selectedFolder))
        for eachPic in newPicsList:
            if '-a.' in eachPic:
                newPicName = eachPic.replace('-a', '_id1')
                os.rename(os.path.join('database', selectedFolder, eachPic), os.path.join('database', selectedFolder, newPicName))
            elif '-c.' in eachPic:
                newPicName = eachPic.replace('-c', '_id2')
                os.rename(os.path.join('database', selectedFolder, eachPic), os.path.join('database', selectedFolder, newPicName))
            else:
                pass

    if len(allPeopleList) == 0:
        break






