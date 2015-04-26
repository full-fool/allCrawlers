#coding=utf-8
import random
import os
import sys
import uuid
import shutil


try:
    meituPath = sys.argv[1]
    targetPath = sys.argv[2]
except Exception as ep:
    print 'wrong argument, meituName, targetPath'
    sys.exit()


if not os.path.exists(meituPath):
    print 'cannot find meitu'
    sys.exit()




noiseNum = 100000

os.chdir(targetPath)


if not os.path.exists('noise'):
    os.makedirs('noise')

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





