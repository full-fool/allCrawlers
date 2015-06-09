#coding=utf-8
import sys
import urllib2, urllib
import re
import threading
import time
import os
import socket
import shutil
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3

writeLock = threading.Lock()
writeDoneWorkLock = threading.Lock()


def getListFromFile(fileName):
    try:
        fileLines = open(fileName).read().split('\n')
    except Exception as ep:
        writeToLog('wrong with list file,%s' % fileName)
        return None
    
    picsUrlList = []

    for line in fileLines:
        if line == '\n' or line == '\r' or line == '':
            continue
        picsUrlList.append(line)


    return picsUrlList


def writeDoneWork(name):
    writeDoneWorkLock.acquire()
    
    filehandler = open('doneWork_downloadPicsTieba.txt', 'a')
    filehandler.write(name+'\n')
    filehandler.close()
    
    writeDoneWorkLock.release()

def getDoneWork():
    if not os.path.exists('doneWork_downloadPicsTieba.txt'):
        return []
    return open('doneWork_downloadPicsTieba.txt').read().split('\n')

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
    def __init__(self, dirName, picListList):
        threading.Thread.__init__(self)
        self.dirName = dirName
        self.picListList = picListList

    def run(self):
        dirName = self.dirName
        picListList = self.picListList
        albumsNum = len(picListList)
        totalNum = 0
        while totalNum < 1000:
            allEmpty = True
            for i in range(albumsNum):
                if len(picListList[i]) == 0:
                    continue
                allEmpty = False

                picUrl = picListList[i][0]
                picName = picUrl.split('/')[-1]
                picPath = os.path.join(dirName, picName)
                picListList[i].remove(picUrl)
                totalNum += 1
                try:
                    urllib.urlretrieve(picUrl, picPath)
                except Exception as ep:
                    writeToLog('cannot download pic for,%s,%s,%s' % (dirName, picName, picUrl))
                if totalNum == 1000:
                    break
            if allEmpty == True:
                break
        print 'done %s pics for %s' % (totalNum, dirName)
        writeDoneWork(dirName)

        



doneWorkList = getDoneWork()



threadNum = 50
threadNumPool = {}

allDirsList = []
allFilesList = os.listdir('.')
for eachFile in allFilesList:
    if os.path.isdir(eachFile):
        allDirsList.append(eachFile)

for eachNameDir in allDirsList:
    if eachNameDir in doneWorkList:
        print 'already download for,%s' % eachNameDir
        continue
    albumsList = os.listdir(eachNameDir)
    albumsNum = len(albumsList)
    if albumsNum == 0:
        writeToLog('no photos for,%s' % eachNameDir)
        continue 
    picsListList  = []
    for eachAlbum in albumsList:
        picsListPath = os.path.join(eachNameDir, eachAlbum, 'picsUrlList.txt')
        allPicsForOneList = getListFromFile(picsListPath)
        picsListList.append(allPicsForOneList)
        shutil.rmtree(os.path.join(eachNameDir, eachAlbum))

    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = DownloadPicsForOneShop(eachNameDir, picsListList)
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    threadNumPool[j] = DownloadPicsForOneShop(eachNameDir, picsListList)
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)






