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
    if not os.path.exists(os.path.join('database', selectedFolder)):
        os.makedirs(os.path.join('database', selectedFolder))
    originalPicsList = os.listdir(os.path.join(datasetPath, selectedFolder))
    for eachOriPic in originalPicsList:
        if '_i_01_00_00_HP_00.' in eachOriPic:
            newPicName = eachOriPic.replace('_i_01_00_00_HP_00', '_i_01_00_00_HP_00_id1')
            shutil.copyfile(os.path.join(datasetPath, selectedFolder, eachOriPic), os.path.join('database', selectedFolder, newPicName))

    #shutil.copytree(os.path.join(datasetPath, selectedFolder), os.path.join('database', selectedFolder))

    if len(allPeopleList) == 0:
        break






