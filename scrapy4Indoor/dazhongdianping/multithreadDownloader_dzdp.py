#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import json
import threading
import time
import os
import socket
from bs4 import BeautifulSoup
import uuid
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3

writeLock = threading.Lock()
writeDoneWorkLock = threading.Lock()

def robustPrint(content):
    try:
        print content
    except Exception as ep:
        print ep.message

def getListFromFile(fileName):
    picsUrlList = []
    for line in open(fileName):
        if line == '\n' or line == '\r' or line == '':
            continue
        picName = line.split(',')[0]
        picUrl = ''.join(line.split(',')[1:])
        picsUrlList.append((picName, picUrl))

    return picsUrlList


def writeDoneWork(name):
    writeDoneWorkLock.acquire()
    
    filehandler = open('doneWork.txt', 'a')
    filehandler.write(name+'\n')
    filehandler.close()
    
    writeDoneWorkLock.release()

def getDoneWork():
    if not os.path.exists('doneWork.txt'):
        return []
    return open('doneWork.txt').read().split('\n')

def writeToLog(content):
    writeLock.acquire()

    try:
        print content
    except Exception as ep:
        print ep.message
    filehandler = open('log_downloader.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()

    writeLock.release()


class DownloadPicsForOneShop(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, dirName):
        threading.Thread.__init__(self)
        self.dirName = dirName

    def run(self):
        dirName = self.dirName
        dishPicsFilePath = os.path.join(dirName, 'dishPicUrlList.txt')
        environPicsFilePath = os.path.join(dirName, 'environPicUrlList.txt')
        try:
            dishPicsUrlList = getListFromFile(dishPicsFilePath)
        except Exception as ep:
            writeToLog('dish file not found,%s' % str(dishPicsFilePath))
            writeDoneWorkLock(dirName)
            return 
        for eachDishPic in dishPicsUrlList:
            if not os.path.exists(os.path.join(dirName, 'dish')):
                os.makedirs(os.path.join(dirName, 'dish'))
            dishName = eachDishPic[0]
            dishPicUrl = eachDishPic[1]
            picPath = os.path.join(dirName, 'dish', dishName.encode('gbk'))
            try:
                urllib.urlretrieve(dishPicUrl, picPath)
                robustPrint('download one dish pic for %s,%s' % (dirName, dishPicUrl))
            except Exception as ep:
                writeToLog('cannot download dish pic,%s,%s' % (dishPicUrl, dirName))
        robustPrint('done pics for dish,%s' % dirName)

        try:
            environPicsUrlList = getListFromFile(environPicsFilePath)
        except Exception as ep:
            writeToLog('environ file not found,%s' % str(environPicsFilePath))
            writeDoneWorkLock(dirName)
            return
        for eachEnvironPic in environPicsUrlList:
            if not os.path.exists(os.path.join(dirName, 'environment')):
                os.makedirs(os.path.join(dirName, 'environment'))
            environName = eachEnvironPic[0]
            environPicUrl = eachEnvironPic[1]
            picPath = os.path.join(dirName, 'environment', environName.encode('gbk'))
            try:
                urllib.urlretrieve(environPicUrl, picPath)
                robustPrint('download one environment pic for %s,%s' % (dirName, environPicUrl))
            except Exception as ep:
                writeToLog('cannot download environment pic,%s,%s' % (environPicUrl, dirName))
        robustPrint('done pics for environment,%s' % dirName)
        writeDoneWork(dirName)
        





doneWorkList = getDoneWork()
# getListFromFile('dishPicUrlList.txt')



allDirsList = []
allFilesList = os.listdir('.')
for eachFile in allFilesList:
    if os.path.isdir(eachFile) and not eachFile in doneWorkList:
        allDirsList.append(eachFile)




threadNum = 10
threadNumPool = {}





for i in range(len(allDirsList)):
    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = DownloadPicsForOneShop(allDirsList[i])
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    #threadNumPool[j].stop()
                    threadNumPool[j] = DownloadPicsForOneShop(allDirsList[i])
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)









