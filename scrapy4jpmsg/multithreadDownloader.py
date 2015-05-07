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


class DownloadPicsForOnePeople(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, dirName):
        threading.Thread.__init__(self)
        self.dirName = dirName

    def run(self):
        dirName = self.dirName
        picsFilePath = os.path.join(dirName, 'picsUrlList.txt')
        try:
            picsUrlList = getListFromFile(picsFilePath)
        except Exception as ep:
            writeToLog('file not found,%s' % str(picsFilePath))
            return 
        picNum = 0
        for picUrl in picsUrlList:
            picPath = os.path.join(dirName, '%s.jpg' % picNum)
            try:
                urllib.urlretrieve(picUrl, picPath)
                print 'download one pic for %s,%s' % (dirName, picUrl)
                picNum += 1
            except Exception as ep:
                writeToLog('cannot download pic,%s,%s' % (picUrl, dirName))
        os.rename(dirName, 'jpmsg_' + dirName)

        






allDirsList = []
allFilesList = os.listdir('.')
for eachFile in allFilesList:
    if os.path.isdir(eachFile) and not 'jpmsg_' in eachFile:
        allDirsList.append(eachFile)




threadNum = 100
threadNumPool = {}





for i in range(len(allDirsList)):
    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = DownloadPicsForOnePeople(allDirsList[i])
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    threadNumPool[j] = DownloadPicsForOnePeople(allDirsList[i])
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)









