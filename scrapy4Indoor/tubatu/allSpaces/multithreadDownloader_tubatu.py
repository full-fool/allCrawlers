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
        picID    = line.split(',')[1]
        picUrl = line.split(',')[2]
        picDescription = line.split(',')[3]
        picsUrlList.append((picName, picID, picUrl, picDescription))

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
    def __init__(self, picName, picUrl):
        threading.Thread.__init__(self)
        self.picName = picName
        self.picUrl = picUrl

    def run(self):
        picName = self.picName
        picUrl = self.picUrl
        try:
            urllib.urlretrieve(picUrl, picName)
            writeDoneWork(picName)
            print 'donwload one pic,%s' % picName
        except Exception as ep:
            writeToLog('cannot download pic,%s,%s' % (picName, picUrl))
       
        return      

        

threadNum = 100
threadNumPool = {}


doneWorkList = getDoneWork()


for filePart in os.walk('.'):
    if 'picInfoList.txt' in filePart[2]:
        print 'picInfoList.txt in ' + filePart[0]
        #if filePart[0] in doneWorkList:
        #    print 'already done ' + filePart[0]
        #    continue
        
        filePath = os.path.join(filePart[0], 'picInfoList.txt')
        picList = getListFromFile(filePath)
        for eachPic in picList:
            if eachPic[0] in doneWorkList:
                print 'already download pic %s' % eachPic[0]
                continue
            findThread = False
            while findThread == False:
                for j in range(threadNum):
                    if not threadNumPool.has_key(j):
                        threadNumPool[j] = DownloadPicsForOnekind(eachPic[0], eachPic[2])
                        threadNumPool[j].start()
                        findThread = True
                        break
                    else:
                        if not threadNumPool[j].isAlive():
                            threadNumPool[j] = DownloadPicsForOnekind(eachPic[0], eachPic[2])
                            threadNumPool[j].start()
                            findThread = True
                            break
                if findThread == False: 
                    time.sleep(5)









