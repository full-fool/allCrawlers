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
            alreadyTriedTimes += 1
            if alreadyTriedTimes < tryTimes:
                pass
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
    for line in open(fileName):
        for line2 in line.split('\r'):
            line2 = re.sub(r'\n', '', line2)
            line2 = line2.strip(' ')
            namelist.append(line2)
    return namelist



def getInfoForProduct(url):
    productMainPage = getPageWithSpecTimes(2, url)
    if productMainPage == None:
        writeToLog('cannot open page,%s' % url)
        return

    # try:
    #     productMainPage = urllib.urlopen(url).read().decode('gbk', 'ignore').encode('utf8')
    # except Exception as ep:
        # print ep.message
        # writeToLog('cannot open page,%s' % url)
        # return

    if '京东网上商城' in productMainPage:
        writeToLog('url out of date,%s' % url)
        return

    pagesoup = BeautifulSoup(productMainPage, from_encoding='utf8')

    resultDict = {}
    resultDict['url'] = url
    resultDict['info'] = {}
    resultDict['info']['topInfo'] = []
    #resultDict['info']['detail'] = {}
    #形如 http://item.jd.com/1322433653.html 这样的网页布局
    if 'p-parameter-list' in productMainPage:
        try:
            detailSection = pagesoup.find_all("ul", attrs={"class": 'p-parameter-list'})[0]
        except Exception as ep:
            print ep.message
            writeToLog('cannot find product detail for url,%s' % url)
            return 
        allAttributes = detailSection.find_all('li')
        allAttributesList = {}
        for attribute in allAttributes:
            if attribute.string == None:
                if '店铺' in str(attribute):
                    allAttributesList['店铺'] = attribute.a.string
                else:
                    print 'unknown attribute, %s' % str(attribute)
            else:
                allAttributesList[attribute.string.split('：')[0]] = '：'.join(attribute.string.split('：')[1:])
        resultDict['info']['detail'] = allAttributesList
        # for eachItem in allAttributesList:
        #     print eachItem, allAttributesList[eachItem]




    #形如 http://item.jd.com/1411304215.html 这样的网页布局
    elif 'detail-list' in productMainPage:
        #print 'detail-list in page'
        try:
            detailSection = pagesoup.find_all("ul", attrs={"class": 'detail-list'})[0]
        except Exception as ep:
            print ep.message
            writeToLog('cannot find product detail for url,%s' % url)
            return
        allAttributes = detailSection.find_all('li')
        allAttributesList = {}
        for attribute in allAttributes:
            #厚度：普通
            allAttributesList[attribute.string.split('：')[0]] = '：'.join(attribute.string.split('：')[1:])

        resultDict['info']['detail'] = allAttributesList

        # for eachItem in allAttributesList:
        #    print eachItem, allAttributesList[eachItem]

    #get top info
    allTopInfoItems = pagesoup.find_all('a', attrs={"clstag": re.compile(r'.+?mbNav.+?')})
    if len(allTopInfoItems) == 0:
        print 'no top info for url,%s' % url
    #print len(allTopInfoItems)
    for eachTopItemInfo in allTopInfoItems:
        #print eachTopItemInfo.string
        resultDict['info']['topInfo'].append(eachTopItemInfo.string)



        #print allAttributesList








class FetchInfoForProduct(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url

    def run(self):
        url = self.url
        getInfoForProduct(url)
        



#getInfoForProduct('http://item.jd.com/1333626931.html')
# page = urllib.urlopen('http://item.jd.com/1215987809.html').read().decode('gbk', 'ignore').encode('utf8')
# filehandler = open('temp.html', 'w')
# filehandler.write(page)
# filehandler.close()

allUrlsList = getListFromFile('items.txt')
allUrlsNum = len(allUrlsList)

threadNum = 10
threadNumPool = {}


startProcess = loadProcess()

for i in range(startProcess, len(allUrlsList)):
    setProcess(str(i))
    print 'process: %s/%s' % (i, allUrlsNum)
    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = FetchInfoForProduct(allUrlsList[i])
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    #threadNumPool[j].stop()
                    threadNumPool[j] = FetchInfoForProduct(allUrlsList[i])
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)




