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

def getRedownloadList():
    resultList = []
    fileLines = open('log_downloader.txt').read().split('\n')
    filehandler = open('log_downloader.txt', 'w')
    filehandler.close()
    for eachLine in fileLines:
        if eachLine == '':
            continue
        resultList.append((eachLine.split(',')[1], eachLine.split(',')[2], eachLine.split(',')[3]))


    return resultList


class DownloadPic(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, dirName, picName, picUrl):
        threading.Thread.__init__(self)
        self.dirName = dirName
        self.picName = picName
        self.picUrl = picUrl

    def run(self):
        dirName = self.dirName
        picName = self.picName
        picUrl = self.picUrl
        picPath = os.path.join(dirName, picName)
        try:
            urllib.urlretrieve(picUrl, picPath)
        except Exception as ep:
            writeToLog('cannot download pic,%s,%s,%s' % (dirName, picName, picUrl))






reDownloadList = getRedownloadList()




threadNum = 50
threadNumPool = {}




#'http://imgsrc.baidu.com/forum/pic/item/%s.jpg'
for eachPic in reDownloadList:
    fatherDir = eachPic[0]
    picName = eachPic[1]
    picUrl = eachPic[2]

    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = DownloadPic(fatherDir, picName, picUrl)
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    threadNumPool[j] = DownloadPic(fatherDir, picName, picUrl)
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)




