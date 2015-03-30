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

makeDirLock = threading.Lock()



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


class DownloadPicsForOneDir(threading.Thread):
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
        
        #去重
        downloadList = []
        for eachUrl in picsUrlList:
            if not eachUrl in downloadList:
                downloadList.append(eachUrl)

        picNum = 0
        for picUrl in downloadList:
            picPath = os.path.join(dirName, '%s.jpg' % picNum)
            try:
                filehandler = open(picPath, 'wb')
                picContent = urllib2.urlopen(picUrl).read()
                if 'file not found' in picContent:
                    time.sleep(5)
                    picContent = urllib2.urlopen(picUrl).read()

                if 'file not found' in picContent:
                    writeToLog('cannot download pic because of empty content,%s,%s' % (picUrl, dirName))
                    continue
                filehandler.write(picContent)
                filehandler.close()
                #urllib.urlretrieve(picUrl, picPath)
                print 'download one pic for %s,%s\n' % (dirName, picUrl)
                picNum += 1
            except Exception as ep:
                print ep.message
                writeToLog('cannot download pic,%s,%s' % (picUrl, dirName))
                time.sleep(5)
        
        # 将已经下载过的区分开来
        makeDirLock.acquire()
        os.rename(dirName, 'huafen_' + dirName)
        makeDirLock.release()
        


# picUrl = 'http://huafans.dbankcloud.com/pic/43f7aaa565090e2d5b1122a569e4614810f.jpg?mode=open'
# filehandler = open('testpic.jpg', 'wb')
# picContent = urllib.urlopen(picUrl).read()
# if 'file not found' in picContent:
#     time.sleep(5)
#     print 'file not found'
#     picContent = urllib.urlopen(picUrl).read()

# if 'file not found' in picContent:
#     print 'cannot download pic because of empty content'
#     sys.exit()
# filehandler.write(picContent)
# filehandler.close()
# sys.exit()





allDirsList = []
allFilesList = os.listdir('.')
for eachFile in allFilesList:
    if os.path.isdir(eachFile) and not 'huafen_' in eachFile:
        allDirsList.append(eachFile)




threadNum = 100
threadNumPool = {}





for i in range(len(allDirsList)):
    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = DownloadPicsForOneDir(allDirsList[i])
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    #threadNumPool[j].stop()
                    threadNumPool[j] = DownloadPicsForOneDir(allDirsList[i])
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)









