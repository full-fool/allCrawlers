#coding=utf-8
import random
import os
import sys
import uuid
import shutil


try:
    datasetPath = sys.argv[1]
    meituPath = sys.argv[2]
    targetPath = sys.argv[3]
except Exception as ep:
    print 'wrong argument, datasetName meituName'
    sys.exit()

if not os.path.exists(datasetPath):
    print 'cannot find dataset'
    sys.exit()

if not os.path.exists(meituPath):
    print 'cannot find meitu'
    sys.exit()




noiseNum = 100000

os.chdir(targetPath)

if not os.path.exists('database'):
    os.makedirs('database')

if not os.path.exists('noise'):
    os.makedirs('noise')

allPeopleList = os.listdir(datasetPath)
for eachDir in allPeopleList:
    if not os.path.isdir(os.path.join(datasetPath, eachDir)):
        allPeopleList.remove(eachDir)


# Database
while 1:
    randomSelectedIndex = random.randint(0, len(allPeopleList)-1)
    selectedFolder = allPeopleList[randomSelectedIndex]
    shutil.copytree(os.path.join(datasetPath, selectedFolder), os.path.join('database', selectedFolder))
    allPeopleList.remove(selectedFolder)
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


# Noise from Meitu
alreadySelectedNum = 0
meituPicsList = os.listdir(meituPath)

while 1:
    randomSelectedIndex = random.randint(0, len(meituPicsList)-1)
    selectedPic = meituPicsList[randomSelectedIndex]
    meituPicsList.remove(selectedPic)
    shutil.copyfile(os.path.join(meituPath, selectedPic), os.path.join('noise', noisePic))
    alreadySelectedNum += 1
    if alreadySelectedNum == noiseNum:
        break





