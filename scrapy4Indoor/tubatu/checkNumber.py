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
        picName = line.split(',')[1]
        picUrl = line.split(',')[0]
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


class DownloadPicsForOnekind(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, picList, dirName):
        threading.Thread.__init__(self)
        self.dirName = dirName
        self.picList = picList

    def run(self):
        dirName = self.dirName
        picList = self.picList
        

       
        for eachPic in picList:
            picName = eachPic[0] + '.jpg'
            picUrl = eachPic[1]
            picPath = os.path.join(dirName, picName)

            try:
                urllib.urlretrieve(picUrl, picPath)
                robustPrint('download one pic for %s,%s' % (dirName, picUrl))
            except Exception as ep:
                writeToLog('cannot download pic,%s,%s' % (picUrl, dirName))
        robustPrint('done pics for,%s' % dirName)

      
        writeDoneWork(dirName)
        

threadNum = 100
threadNumPool = {}


doneWorkList = getDoneWork()

totalNum = 0
for filePart in os.walk('.'):
    if 'picsUrlList.txt' in filePart[2]:
        robustPrint('picsUrlList in ' + filePart[0])
        if filePart[0] in doneWorkList:
            robustPrint('already done ' + filePart[0])
            continue
        
        filePath = os.path.join(filePart[0], 'picsUrlList.txt')
        picList = getListFromFile(filePath)

        totalNum += len(picList)
  
print 'totalNum is ' + totalNum






