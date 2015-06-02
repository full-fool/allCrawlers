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
    
    filehandler = open('doneWork_downloadMatchPics.txt', 'a')
    filehandler.write(name+'\n')
    filehandler.close()
    
    writeDoneWorkLock.release()

def getDoneWork():
    if not os.path.exists('doneWork_downloadMatchPics.txt'):
        return []
    return open('doneWork_downloadMatchPics.txt').read().split('\n')

def writeToLog(content):
    writeLock.acquire()

    try:
        print content
    except Exception as ep:
        print ep.message
    filehandler = open('log_matchPicsDownloader.txt', 'a')
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
        filePath = os.path.join(dirName, 'picList.txt')
        itemList = getListFromFile(filePath)
        for eachItem in itemList:
            picName = eachItem[0]
            picPath = os.path.join(dirName, picName)
            picUrl  = eachItem[1]
            try:
                urllib.urlretrieve(picUrl, picPath)
            except Exception as ep:
                writeToLog('cannot downlod match pic,%s,%s,%s' % (dirName, picName, picUrl))

        print 'done match pics for %s' % dirName
        writeDoneWork(dirName)
        







doneWorkList = getDoneWork()


threadNum = 100
threadNumPool = {}



for filePart in os.walk('.'):
    if 'picList.txt' in filePart[2]:
        print 'picList.txt in ' + filePart[0]
        if filePart[0] in doneWorkList:
            print 'already downloaded %s' % filePart[0]
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





