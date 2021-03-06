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
import shutil
from bs4 import BeautifulSoup
import uuid
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')



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
    
    filehandler = open('doneWork_downloadPicsRenren.txt', 'a')
    filehandler.write(name+'\n')
    filehandler.close()
    
    writeDoneWorkLock.release()

def getDoneWork():
    if not os.path.exists('doneWork_downloadPicsRenren.txt'):
        return []
    return open('doneWork_downloadPicsRenren.txt').read().split('\n')

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
        filePath = os.path.join(dirName, 'picsUrlList.txt')
        itemList = getListFromFile(filePath)
        #fatherDir = os.path.split(dirName)[0]
        #print '%s pics for %s' % (len(itemList), dirName)
        for eachItem in itemList:
            picUrl = eachItem
            picName = eachItem.split('/')[-1]
            picPath = os.path.join(dirName, picName)
            try:
                urllib.urlretrieve(picUrl, picPath)
            except Exception as ep:
                writeToLog('cannot download pic,%s,%s,%s' % (dirName, picName, picUrl))
        writeDoneWork(dirName)
        doneFilePath = os.path.join(dirName, 'picsUrlList_done.txt')
        os.rename(filePath, doneFilePath)
        #shutil.rmtree(dirName) 
        print 'done for %s' % dirName






doneWorkList = getDoneWork()



threadNum = 50
threadNumPool = {}




#'http://imgsrc.baidu.com/forum/pic/item/%s.jpg'

for filePart in os.walk('.'):
    if 'picsUrlList.txt' in filePart[2]:
        print 'picsUrlList.txt in ' + filePart[0]
        if filePart[0] in doneWorkList:
            print 'already done for %s' % filePart[0]
            continue
        findThread = False
        while findThread == False:
            for j in range(threadNum):
                if not threadNumPool.has_key(j):
                    threadNumPool[j] = DownloadPicsForOneShop(filePart[0])
                    threadNumPool[j].start()
                    findThread = True
                    break
                else:
                    if not threadNumPool[j].isAlive():
                        threadNumPool[j] = DownloadPicsForOneShop(filePart[0])
                        threadNumPool[j].start()
                        findThread = True
                        break
            if findThread == False: 
                time.sleep(5)




