#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import json
import os
import socket
from bs4 import BeautifulSoup
import time
import threading
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3

writeLock = threading.Lock()
logLock = threading.Lock()

doneWorkList = []
def loadProcess():
    try:
        carBrandNum = int(open('process.txt').read())
        return carBrandNum
    except Exception as ep:
        print 'wrong with the process.txt'
        sys.exit()

def setProcess(process):
    filehandler = open('process.txt', 'w')
    filehandler.write(process)
    filehandler.close()


#type 0,justopen, 1,gb2312, 2,gbk, 3,GBK, 4,utf-8
def getPageWithSpecTimes(decodeType, url):
    tryTimes = 4
    alreadyTriedTimes = 0
    html = None
    while alreadyTriedTimes < tryTimes:
        try:
            if decodeType == 0:
                html = urllib2.urlopen(url).read()                
            elif decodeType == 1:
                html = urllib2.urlopen(url).read().decode('gb2312', 'ignore').encode('utf8')
            elif decodeType == 2:
                html = urllib2.urlopen(url).read().decode('gbk', 'ignore').encode('utf8')
            elif decodeType == 3:
                html = urllib2.urlopen(url).read().decode('GBK', 'ignore').encode('utf8')
            else:
                html = urllib2.urlopen(url).read()
            break
        except Exception as ep:
            print ep.message
            alreadyTriedTimes += 1
            if alreadyTriedTimes == 1:
                time.sleep(1)
            elif alreadyTriedTimes == 2:
                time.sleep(60)
            elif alreadyTriedTimes == 3: 
                time.sleep(300)
            else:
                return None
    return html


def writeToLog(content):
    try:
        print content
    except Exception as ep:
        print ep.message

    logLock.acquire()
    filehandler = open('log.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()
    logLock.release()



def getListFromFile(fileName):
    namelist = []
    contentList = open(fileName).read().split('\n')
    for eachLine in contentList:
        namelist.append((eachLine.split(',')[0], eachLine.split(',')[1], eachLine.split(',')[2]))
    return namelist

def loadDoneWork():
    contentList = open('donework.txt').read().split('\n')
    return contentList



class DownloadLinkForOneClothes(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, gender, clothesType, pageUrl):
        threading.Thread.__init__(self)
        self.gender = gender
        self.clothesType = clothesType
        self.pageUrl = pageUrl

    def run(self):
        gender = self.gender
        clothesType = self.clothesType
        pageUrl = self.pageUrl


        getTypeAndStyle(gender, clothesType, pageUrl)
        print 'thread is done for,%s,%s,%s' % (gender, clothesType, pageUrl)






def getTypeAndStyle(gender, clothesType, url):
    print gender, clothesType
    pageContent = getPageWithSpecTimes(0, url)
    if pageContent == None:
        writeToLog('cannot open page for,%s,%s,%s' % (gender, clothesType, url))
        return None

    if not os.path.exists(os.path.join(gender, clothesType)):
        os.makedirs(os.path.join(gender, clothesType))


    itemPattern = re.compile(r'<a target="_blank" href="http://item\.jd\.com/(\d+?).html" onclick="')
    itemIDList = itemPattern.findall(pageContent)
    
    filehandler = open(os.path.join(gender, clothesType, 'itemList.txt'), 'a')    
    for eachItem in itemIDList:
        filehandler.write(eachItem+'\n')
    filehandler.close()
    
    currentPageNum = 1
    while '下一页' in pageContent:
        currentPageNum += 1
        print currentPageNum
        pageUrl = url + '&page=%s' % currentPageNum
        pageContent = getPageWithSpecTimes(0, pageUrl)
        if pageContent == None:
            writeToLog('cannot open clothes for some page,%s,%s,%s,%s' % (gender, clothesType, currentPageNum, pageUrl))
            continue
        addedItemIdList = itemPattern.findall(pageContent)
        filehandler = open(os.path.join(gender, clothesType, 'itemList.txt'), 'a')    
        for eachItem in addedItemIdList:
            filehandler.write(eachItem+'\n')
        filehandler.close()



#getTypeAndStyle('m','羽绒服','http://list.jd.com/1315-1342-3982.html')
#sys.exit()


threadNum = 100
threadNumPool = {}

def findThread(gender, clothesType, pageUrl):
    global threadNum
    global threadNumPool
    findThread = False
    while findThread == False:
        for k in range(threadNum):
            if not threadNumPool.has_key(k):
                threadNumPool[k] = DownloadLinkForOneClothes(gender, clothesType, pageUrl)
                threadNumPool[k].start()
                findThread = True
                break
            else:
                if not threadNumPool[k].isAlive():
                    #threadNumPool[j].stop()
                    threadNumPool[k] = DownloadLinkForOneClothes(gender, clothesType, pageUrl)
                    threadNumPool[k].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)


furnitureList = getListFromFile('linkList.txt')
for eachFurniture in furnitureList:
    findThread(eachFurniture[0], eachFurniture[1], eachFurniture[2])
