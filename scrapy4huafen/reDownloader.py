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



def getListFromFile(fileName):
    picsUrlList = []
    for line in open(fileName):
        for line2 in line.split('\r'):
            line2 = re.sub(r'\n', '', line2)
            if line2 != '':
                picsUrlList.append(line2)

    return picsUrlList

def loadProcess():
    try:
        return int(open('process_redownloader.txt').read())
    except Exception as ep:
        print 'something wrong with the process txt'
        sys.exit()

def setProcess(process):
    filehandler = open('process_redownloader.txt','w')
    filehandler.write(process)
    filehandler.close()


def writeToLog(content):
    writeLock.acquire()

    try:
        print content
    except Exception as ep:
        print ep.message
    filehandler = open('log_redownloader.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()


    writeLock.release()

class DownloadOnePic(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, dirName, picUrl):
        threading.Thread.__init__(self)
        self.dirName = dirName
        self.picUrl = picUrl

    def run(self):
        dirName = self.dirName
        picUrl = self.picUrl

        if not os.path.exists(dirName):
            print 'directory %s does not exist' % dirName
            return

        alreadyHadPicNum = len(os.listdir(dirName))
        picPath = os.path.join(dirName, '%s.jpg' % alreadyHadPicNum)
        try:
            urllib.urlretrieve(picUrl, picPath)
            print 'download one picture for dir,%s' % dirName
        except Exception as ep:
            print ep.message
            writeToLog('cannot download pic,%s,%s' % (dirName, picUrl))



startPoint = loadProcess()

logList = getListFromFile('log_downloader.txt')
reDownloadList = []
for eachLog in logList:
    if 'cannot download pic,' in eachLog:
        reDownloadList.append((eachLog.split(',')[1], eachLog.split(',')[2]))




threadNum = 100
threadNumPool = {}

for i in range(startPoint, len(reDownloadList)):
    setProcess(str(i))
    picUrl = reDownloadList[i][0]
    dirName = 'huafen_' + reDownloadList[i][1]

    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = DownloadOnePic(dirName, picUrl)
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    #threadNumPool[j].stop()
                    threadNumPool[j] = DownloadOnePic(dirName, picUrl)
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)




'''



    if not os.path.exists(dirName):
        print 'directory %s does not exist' % dirName
        continue

    alreadyHadPicNum = len(os.listdir(dirName))
    picPath = os.path.join(dirName, '%s.jpg' % alreadyHadPicNum)
    try:
        urllib.urlretrieve(picUrl, picPath)
        print 'download one picture for dir,%s' % dirName
    except Exception as ep:
        print ep.message
        writeToLog('cannot download pic,%s,%s' % (dirName, picUrl))




'''



