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

CardInfo = {}

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
    tryTimes = 3
    alreadyTriedTimes = 0
    html = None
    while alreadyTriedTimes < tryTimes:
        try:
            if decodeType == 0:
                html = urllib.urlopen(url).read()                
            elif decodeType == 1:
                html = urllib.urlopen(url).read().decode('gb2312', 'ignore').encode('utf8')
            elif decodeType == 2:
                html = urllib.urlopen(url).read().decode('gbk', 'ignore').encode('utf8')
            elif decodeType == 3:
                html = urllib.urlopen(url).read().decode('GBK', 'ignore').encode('utf8')
            else:
                html = urllib.urlopen(url).read()
            break
        except Exception as ep:
            if alreadyTriedTimes < tryTimes - 1:
                alreadyTriedTimes += 1
                pass
            else:
                return None
    return html

def writeToLog(content):
    writeLock.acquire()

    try:
        print content
    except Exception as ep:
        print ep.message
    filehandler = open('log.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()

    writeLock.release()


class DownloadOnePagePeople(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, pageUrl):
        threading.Thread.__init__(self)
        self.pageUrl = pageUrl

    def run(self):
        pageUrl = self.pageUrl
        resultCardLinkList = getAllCardLinks(pageUrl)
        for cardLink in resultCardLinkList:
            downLoadPic(cardLink)
        


def getAllCardLinks(url):
    try:
        pageContent = urllib.urlopen(url).read().decode('gb2312', 'ignore').encode('utf8')
    except Exception as ep:
        print ep.message
        writeToLog('cannot open page,%s' % url)
        return

    cardLinkPattern = re.compile(r'href="(/cardapply/channel/indexUnionPay/card\?cardId=[\d]+)"')
    cardLinkList = cardLinkPattern.findall(pageContent)[6:]
    cardLinkList = list(set(cardLinkList))
    resultCardLinkList = []
    #https://shenka.95516.com/cardapply/channel/indexUnionPay/card?cardId=2
    for cardLink in cardLinkList:
        resultCardLinkList.append('https://shenka.95516.com' + cardLink)
    #print cardLinkList
    #print len(cardLinkList)
    return resultCardLinkList



def downLoadPic(url):
    global CardInfo
    try:
        pageContent = urllib.urlopen(url).read()
    except Exception as ep:
        print ep.message
        writeToLog('cannot open card,%s' % url)
        return
    imgLinkPattern = re.compile(r'<div class="cardcd01 ml30" ><img  src="([^"]+?)"') 
    try:
        imgLink = imgLinkPattern.findall(pageContent)[0]
    except Exception as ep:
        print ep.message
        writeToLog('cannot find card url,%s' % url)
        return

    imgSuffix = imgLink.split('.')[-1]

    cardNamePattern = re.compile(r'<li class=" cardint ml" style="width:500px;">(.+?)</li>')
    try:
        cardName = cardNamePattern.findall(pageContent)[0]
    except Exception as ep:
        print ep.message
        writeToLog('cannot find card name,%s' % url)
        return

    if not CardInfo.has_key(cardName):
        CardInfo[cardName] = 0
    else:
        CardInfo[cardName] += 1
    newCardName = '%s_%s.%s' % (cardName, CardInfo[cardName], imgSuffix)

    try:
        urllib.urlretrieve(imgLink, newCardName)
        print newCardName
    except Exception as ep:
        print 'cannot download pic,%s,%s,%s' % (imgLink, newCardName)



threadNum = 9
threadNumPool = {}

for i in range(1, 10):

    pageUrl = 'https://shenka.95516.com/cardapply/channel/indexUnionPay/list?page=%s' % i

    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = DownloadOnePagePeople(pageUrl)
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    threadNumPool[j] = DownloadOnePagePeople(pageUrl)
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)









