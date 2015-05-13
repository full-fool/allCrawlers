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


def getRedownloadList():
    try:
        fileContent = open('log_downloader.txt').read().split('\n')
    except Exception as ep:
        print 'cannot open log_downloader'
        sys.exit()
    downloadPicList = []
    for eachLine in fileContent:
        if eachLine == '\n' or eachLine == '\r' or eachLine == '':
            continue
        picUrl = eachLine.split(',')[1]
        picPath = eachLine.split(',')[2]
        downloadPicList.append((picUrl, picPath))

    return downloadPicList




class DownloadPicsForOnekind(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, picUrl, picName, picPath):
        threading.Thread.__init__(self)
        self.picUrl = picUrl
        self.picName = picName
        self.picPath = picPath

    def run(self):
        picName = self.picName
        picUrl = self.picUrl
        picPath = self.picPath

        try:
            urllib.urlretrieve(picUrl, picName)
            print 'download one pic for %s' % picPath
        except Exception as ep:
            writeToLog('cannot download pic,%s,%s' % (picUrl, picPath))
            

           

        


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






picList = getRedownloadList()

filehandler = open('log_downloader.txt', 'w')
filehandler.close()


threadNum = 100
threadNumPool = {}



for i in range(len(picList)):
    picUrl = picList[i][0]
    suffix = picUrl.split('.')[-1]
    picPath = picList[i][1]
    picName = os.path.join(picList[i][1], 're_%s.%s' % (i, suffix))
    if not os.path.exists(picPath):
        os.makedirs(picPath)


    findThread = False
    while findThread == False:
        for threadIter in range(threadNum):
            if not threadNumPool.has_key(threadIter):
                threadNumPool[threadIter] = DownloadPicsForOnekind(picUrl,  picName, picPath)
                threadNumPool[threadIter].start()
                findThread = True
                break
            else:
                if not threadNumPool[threadIter].isAlive():
                    threadNumPool[threadIter] = DownloadPicsForOnekind(picUrl,  picName, picPath)
                    threadNumPool[threadIter].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)



